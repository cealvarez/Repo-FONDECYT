__author__ = 'Tania'

import Reader
from datetime import datetime
import Graph as Gr
import operator
import numpy as np


#events_list = inactivity_identification(Reader.patients, time)

def start(file, timestart, timefinish):
    Reader.readLog(file, timestart, timefinish)

# Identifies groups of professionals who attended the same patient at a given time window (hours)
def implicit_tuples(appointments, hours):
    tuples = {}
    total = 0
    maxi = 0
    for patient in appointments:
        events = appointments[patient]
        first = 0
        tuple = {events[first].executor}
        for i in range(len(appointments[patient])-1):
            if days_between(events[first].time, events[i+1].time) < hours: # Cambiar x HOURS BETWEEN
                tuple = tuple | ({events[i+1].executor})
            else:
                if len(tuple) == 1:
                    continue
                tuple = frozenset(tuple)
                if tuple not in tuples:
                    tuples[tuple] = 0
                tuples[tuple] += 1
                maxi = max(tuples[tuple], maxi)
                total += 1
                first = i+1
                tuple = {events[first].executor}

    print("Total de tuplas: ", total, "\nTupla mas repetida: ", maxi, '\n')
    for t in sorted(tuples):
        print(t, '\t\t\t', tuples[t]*100/maxi, '%', '\t\t\t', tuples[t]*100/total)


# days refers to the time window to be considered as inactivity
def inactivity_identification(appointments, days):
    events_list = []
    sub_list = []
    for patient in appointments:
        length = len(appointments[patient])
        events = appointments[patient]
        events[0].set_trigger(True)
        sub_list = [events[0]]
        for i in range(length-1):
            if days_between(events[i].time, events[i+1].time) > days:
                events[i+1].set_trigger(True)

                if len(sub_list) > 0:
                    events_list.append(sub_list)
                sub_list = [events[i+1]]

            else:
                events[i+1].set_trigger(False)
                sub_list.append(events[i+1])
        events_list.append(sub_list)
    return events_list



def implicit_derivation(appointments, days): #MIN 1 dia, dentro del mismo dia no cuenta
    inactivity_identification(appointments, days)
    triggers = {}
    aux = set()
    key = 0
    for patient in appointments:
        events = appointments[patient]
        for e in events:
            if e.is_trigger:
                if key != 0:
                    if aux == set():
                        continue
                    aux = frozenset(aux)
                    if aux not in triggers[key]:
                        triggers[key][aux] = 0
                    triggers[key][aux] += 1
                    aux = set()
                if e.estate not in triggers: # executor or act
                    triggers[e.estate] = {} # executor or act
                    key = e.estate
            else:
                aux = aux | {e.act}
    if key != 0:
        if aux != set():
            aux = frozenset(aux)
            if aux not in triggers[key]:
                triggers[key][aux] = 0
            triggers[key][aux] += 1
            aux = set()

    print("Total de tuplas: ", "", "\nTupla mas repetida: ", "", '\n')
    res = {}
    for t in triggers:
        print(t)
        for d in triggers[t]:
            print('\t', d, " ", triggers[t][d])
            lista = []
            for i in d:
                print(i)
                lista.append(i)
            res[t] = lista
    print (res)


def derivation(events_list):
    relations = {}
    dev = {}

    for events in events_list:
        for i in range(len(events)-1):
            for j in range(len(events)-i-1):
                if(events[i].act == events[i+j+1].act):
                    break
                tuple = (events[i].act, events[i+j+1].act)

                if tuple not in relations:
                    relations[tuple] = 0
                relations[tuple] += 1
                if(events[i].act == 'ECG' or events[i].act == 'LABORATORIO'):
                    continue
                if events[i].act not in dev:
                    dev[events[i].act] = 0
                dev[events[i].act] += 1

    return relations, dev

def derivationEstate(events_list):
    relations = {}
    dev = {}
    for events in events_list:
        for i in range(len(events)-1):
            anterior = ''
            for j in range(len(events)-i-1):

                ###ELIMINA LAS DERIVACIONES ENTRE SALAS DE PROCEDIMIENTO###
                if(events[i].estate == events[i+j+1].estate == 'SALA DE PROCEDIMIENTOS'):
                    continue

                tuple = (events[i].estate, events[i+j+1].estate)
                if tuple not in relations:
                    relations[tuple] = 0
                relations[tuple] += 1

                ###NO SE CUENTAN LAS RELACIONES QUE SALEN DE ESTOS NODOS, YA QUE EN TEORIA NO DEBERIAN GATILLAR DERIVACIONES
                if(events[i].estate == 'ADMINISTRADOR' or events[i].estate == 'ADMINISTRATIVO' or events[i].estate == 'SALA DE PROCEDIMIENTOS'):
                    continue
                if events[i].estate not in dev:
                    dev[events[i].estate] = 0
                dev[events[i].estate] += 1

    return relations, dev


def derivationExecutor(events_list):
    relations = {}
    dev = {}
    anterior = ''

    for events in events_list:
        for i in range(len(events)-1):
            anterior = ''
            for j in range(len(events)-i-1):

                ###SE CORTA SI SE ENCUENTRA AL MISMO PROFESIONAL. ELIMINA LOS AUTOARCOS
                if(events[i].executor == events[i+j+1].executor):
                    break

                ###ELIMINA LAS DERIVACIONES ENTRE SALAS DE PROCEDIMIENTO###
                if(events[i].estate == events[i+j+1].estate == 'SALA DE PROCEDIMIENTOS'):
                    continue

                ###VERIFICA QUE UN PROFESIONAL 'A' NO DERIVE VARIAS VECES A UN PROFESIONAL 'B' SI 'B' VIENE SEGUIDO DE 'A' EN MULTIPLES OCASIONES
                if events[i+j+1].executor == anterior:
                    continue

                tuple = (events[i].executor, events[i+j+1].executor)
                anterior = events[i+j+1].executor
                if tuple not in relations:
                    relations[tuple] = 0
                relations[tuple] += 1
                if(events[i].executor in Reader.role_dic['ADMINISTRADOR'] or events[i].executor in Reader.role_dic['ADMINISTRATIVO'] or events[i].executor in Reader.role_dic['SALA DE PROCEDIMIENTOS']):
                    continue
                if events[i].executor not in dev:
                    dev[events[i].executor] = 0
                dev[events[i].executor] += 1

    return relations, dev

# Returns the number of days between two dates
def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y/%m/%d %H:%M")
    d2 = datetime.strptime(d2, "%Y/%m/%d %H:%M")

    return abs((d2 - d1).days)


# Returns the number of hours between two dates
def hours_between(d1, d2):
    # d2 = datetime.strptime("2014-06-28 12:20:00", "%Y-%m-%d %H:%M:%S")
    d1 = datetime.strptime(d1, "%Y-%m-%d %H:%M:%S")
    d2 = datetime.strptime(d2, "%Y-%m-%d %H:%M:%S")
    return abs((d2 - d1)).total_seconds() // 3600

def resource_freq():
    return Reader.res_names

def estate_freq():
    return Reader.estate_names

def activity_freq():
    return Reader.act_names

def role_groups():
    return Reader.role_dic


#implicit_derivation(Reader.patients, 15)
def showImplicitDerivation(time, mode, threshold, arrow, frequency, global_freq, info):
    events_list = inactivity_identification(Reader.patients, time)
    if mode == 0:
        relaciones, derivaciones = derivation(events_list)
        Gr.show_implicit_derivation(relaciones, activity_freq(), derivaciones, threshold, time, arrow, frequency, global_freq, less_info = info)
    elif mode == 1:
        relaciones, derivaciones = derivationExecutor(events_list)
        Gr.show_implicit_derivation_role(relaciones, resource_freq(), derivaciones, role_groups(), threshold, time, arrow, frequency, global_freq, less_info = info)
    elif mode == 2:
        relaciones, derivaciones = derivationEstate(events_list)
        Gr.show_implicit_derivation_role(relaciones, estate_freq(), derivaciones, role_groups(), threshold, time, arrow, frequency, global_freq, less_info = info)

def showduo(time, threshold, frequency, res_freq, info):
    event_list = inactivity_identification(Reader.patients, time)
    relations = {}
    for events in event_list:
        for i in range(len(events) - 1):
            if(events[i].act == 'G_DUPLAS' and events[i+1].act == 'G_DUPLAS' and events[i].executor != events[i+1].executor and events[i].time == events[i+1].time):
                tuple = (events[i].executor, events[i+1].executor)
                if tuple not in relations:
                    relations[tuple] = 0
                relations[tuple] += 1

            if (i == len(events) - 2):
                continue

            if(events[i].act == 'G_DUPLAS' and events[i+2].act == 'G_DUPLAS' and events[i].executor != events[i+2].executor and events[i].time == events[i+2].time):
                tuple = (events[i].executor, events[i+2].executor)
                if tuple not in relations:
                    relations[tuple] = 0
                relations[tuple] += 1


    daux = sorted(relations.items(), key=operator.itemgetter(1))

    lista = resource_freq()
    for i in lista.keys():
        if lista[i] < frequency:
            del lista[i]
    writer= open('Reports/Duo_relation_frequency.txt', 'w')
    for i in daux:
        if i[0][0] not in lista or i[0][1] not in lista:
            del relations[(str(i[0][0]),str(i[0][1]))]
            if info:
                continue
        elif i[1] < res_freq:
            del relations[(str(i[0][0]),str(i[0][1]))]
            if info:
                continue
        writer.write(str(i[0][0]) + '->' + str(i[0][1]) + ':' + str(i[1]) + '\n')
    writer.write('\n\nSum: ' + str(np.sum(list(relations.values())))+'\nMean: ' + str(round(np.mean(list(relations.values())),3)) + '\nSD: ' + str(round(np.std(list(relations.values())),3)))
    writer.close()

    Gr.showDuo(relations, lista, role_groups(), threshold, frequency, res_freq, time)

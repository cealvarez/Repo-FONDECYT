__author__ = 'Tania'

import Reader
from datetime import datetime, timedelta
import Graph as Gr
import operator
import numpy as np
import Statistics
import math

# events_list = inactivity_identification(Reader.patients, time)

times = 0

# Elements returned by Read.read_log
# Key: cluster. Value: dictionary with the number of cv controls per patient, for patients with more controls than some
# threshold.
most_cv_freq = []
log_patients = {}

# Explicit referrals
# Element returned by Reader.read_referrals
next_appointment = {}


def read_files(clusters_file, clusters, log_file, referrals_file, start, finish, cv_freq):
    global log_patients, most_cv_freq, next_appointment
    # Reader.restart()
    Reader.read_clusters(clusters_file, clusters)
    log_patients, most_cv_freq, next_appointment = Reader.read_log(log_file, start, finish, cv_freq)
    #next_appointment = Reader.read_referrals(referrals_file, start, finish)


# REVISE
# For a specific cluster: identifies groups of professionals who attended the same patient at a given time window (hrs)
def implicit_tuples(cluster, hours):
    tuples = {}
    total = 0
    maxi = 0

    for patient in log_patients[cluster]:
        events = log_patients[cluster][patient]
        first = 0
        professionals_tuple = {events[first].executor}
        for i in range(len(log_patients[cluster][patient])-1):
            if hours_between(events[first].time, events[i+1].time) <= hours:
                professionals_tuple = professionals_tuple | ({events[i+1].executor})
            else:
                if len(professionals_tuple) == 1:
                    continue
                professionals_tuple = frozenset(professionals_tuple)
                if professionals_tuple not in tuples:
                    tuples[professionals_tuple] = 0
                tuples[professionals_tuple] += 1
                maxi = max(tuples[professionals_tuple], maxi)
                total += 1
                first = i+1
                professionals_tuple = {events[first].executor}

    print("Total de tuplas: ", total, "\nTupla mas repetida: ", maxi, '\n')
    for t in sorted(tuples):
        print(t, '\t\t\t', tuples[t]*100/maxi, '%', '\t\t\t', tuples[t]*100/total)


# identifies trigger activities [0] and the triggered activities [1...] and returns a list with these activities
# days refers to the time window to be considered as inactivity
def inactivity_identification(cluster, days):
    events_list = []
    for patient in log_patients[cluster]:
        length = len(log_patients[cluster][patient])
        events = log_patients[cluster][patient]
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


# REVISE
# identifies activities that were executed within a time window (days)
def implicit_derivation(cluster, days):
    inactivity_identification(cluster, days)
    triggers = {}
    aux = set()
    key = 0
    for patient in log_patients[cluster]:
        events = log_patients[cluster][patient]
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
                if e.estate not in triggers:  # executor or act
                    triggers[e.estate] = {}  # executor or act
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

#####################################################################################################################
# Function: derivation/derivation_estate/derivation_executor                                                        #
# returns a dictionary (relations) with KEY: a tuple (A,B) of nodes and VALUE: the # of times that B appears        #
# immediately after A; and a dictionary (referrals) with KEY: a tuple (A,B) of nodes and VALUE: the # of times that #
# B appears sometime after A                                                                                        #
#                                                                                                                   #
# events_list = list of list ([0 = trigger activity, 1.. = following activities])                                   #
#####################################################################################################################
def derivation(cluster, events_list):
    global most_cv_freq
    relations = {}
    referrals = {}
    in_rel = {}
    out_rel = {}
    invalid_acts = []
    reader = open('Input/No_Suma_Act.txt', 'r')

    for line in reader:
        invalid_acts.append(line.strip())
    reader.close()

    statistic_dic = {}
    times_per_patient = {}
    for events in events_list:
        times_per_patient.clear()
        for i in range(len(events)-1):
            for j in range(len(events)-i-1):
                if str(events[i].patient) not in most_cv_freq[cluster]:
                    break
                if str(events[j].patient) not in most_cv_freq[cluster]:
                    continue
                if events[i].act in invalid_acts or events[i+j+1].act in invalid_acts:
                    continue
                if events[i].act == events[i+j+1].act:
                    break
                act_tuple = (events[i].act, events[i+j+1].act)
                if act_tuple not in times_per_patient:
                    times_per_patient[act_tuple] = 0
                times_per_patient[act_tuple] += 1
                if act_tuple not in relations:
                    relations[act_tuple] = 0
                    statistic_dic[act_tuple] = {}
                time_between = days_between(events[i+j+1].time, events[i].time)
                if time_between == 0:
                    time_between = 1
                relations[act_tuple] += 1/time_between

                if events[i].act == 'ECG' or events[i].act == 'LABORATORIO':
                    continue
                if events[i].act not in referrals:
                    referrals[events[i].act] = 0
                referrals[events[i].act] += 1

                if events[i].act not in out_rel:
                    out_rel[events[i].act] = 0
                out_rel[events[i].act] += 1

                if events[i+j+1].act not in in_rel:
                    in_rel[events[i+j+1].act] = 0
                in_rel[events[i+j+1].act] += 1

        for k in times_per_patient:
            if times_per_patient[k] not in statistic_dic[k]:
                statistic_dic[k][times_per_patient[k]] = 0
            statistic_dic[k][times_per_patient[k]] += 1
    file = 'Reports/Statistics/ID_Act_Statistics' + str(cluster) + '.txt'
    writer = open(file, 'w')
    writer.write('(nodo1, nodo2): (veces/paciente, frecuencia)\n')
    for k in statistic_dic:
        writer.write(str(k) + ': ')
        for i in statistic_dic[k]:
            writer.write('(' + str(i) + ',' + str(statistic_dic[k][i]) + ') ')
        writer.write('\n')
    return relations, referrals, in_rel, out_rel, statistic_dic


def derivation_estate(cluster, events_list):
    relations = {}
    referrals = {}
    reader = open('Input/Explicit_Derivation.txt', 'r')
    invalid_roles = []
    for line in reader:
        invalid_roles.append(line.strip())
    reader.close()
    reader2 = open('Input/No_Suma_Act.txt', 'r')
    invalid_acts = []
    for line in reader2:
        invalid_acts.append(line.strip())
    reader2.close()

    statistic_dic = {}
    times_per_patient = {}
    implicit_referrals_per_patient = {}
    for events in events_list:
        times_per_patient.clear()
        for i in range(len(events)-1):
            for j in range(len(events)-i-1):

                if events[i].act in invalid_roles and events[i+j+1].act in invalid_roles:
                    continue

                # removes referrals related to 'SALA DE PROCEDIMIENTOS'
                if events[i].estate == 'SALA DE PROCEDIMIENTOS' or events[i+j+1].estate == 'SALA DE PROCEDIMIENTOS':
                    continue

                # removes relations related to ' TECNICO PARAMEDICO'
                if events[i].estate == 'TECNICO PARAMEDICO' or events[i+j+1].estate == 'TECNICO PARAMEDICO':
                    continue

                # removes relations related to ' ADMINISTRADOR(TIVO'
                if events[i].estate == 'ADMINISTRADOR' or events[i+j+1].estate == 'ADMINISTRADOR':
                    continue
                if events[i].estate == 'ADMINISTRATIVO' or events[i+j+1].estate == 'ADMINISTRATIVO':
                    continue

                if events[i].patient not in implicit_referrals_per_patient:
                    implicit_referrals_per_patient[events[i].patient] = {}
                    implicit_referrals_per_patient[events[i].patient][('MEDICO', 'MEDICO')] = 0
                    implicit_referrals_per_patient[events[i].patient][('MEDICO', 'ENFERMERA')] = 0
                    implicit_referrals_per_patient[events[i].patient][('MEDICO', 'NUTRICIONISTA')] = 0
                    implicit_referrals_per_patient[events[i].patient][('ENFERMERA', 'MEDICO')] = 0
                    implicit_referrals_per_patient[events[i].patient][('ENFERMERA', 'ENFERMERA')] = 0
                    implicit_referrals_per_patient[events[i].patient][('ENFERMERA', 'NUTRICIONISTA')] = 0
                    implicit_referrals_per_patient[events[i].patient][('NUTRICIONISTA', 'MEDICO')] = 0
                    implicit_referrals_per_patient[events[i].patient][('NUTRICIONISTA', 'ENFERMERA')] = 0
                    implicit_referrals_per_patient[events[i].patient][('NUTRICIONISTA', 'NUTRICIONISTA')] = 0
                estate_tuple = (events[i].estate, events[i+j+1].estate)
                if events[i].estate in ['MEDICO', 'ENFERMERA', 'NUTRICIONISTA'] and events[i+j+1].estate in ['MEDICO', 'ENFERMERA', 'NUTRICIONISTA']:
                    implicit_referrals_per_patient[events[i].patient][estate_tuple] += 1
                if estate_tuple not in times_per_patient:
                    times_per_patient[estate_tuple] = 0
                times_per_patient[estate_tuple] += 1
                if estate_tuple not in relations:
                    relations[estate_tuple] = 0
                    statistic_dic[estate_tuple] = {}
                relations[estate_tuple] += 1

                if events[i].estate not in referrals:
                    referrals[events[i].estate] = 0
                referrals[events[i].estate] += 1

            for k in times_per_patient:
                if times_per_patient[k] not in statistic_dic[k]:
                    statistic_dic[k][times_per_patient[k]] = 0
                statistic_dic[k][times_per_patient[k]] += 1

    
    file = 'Reports/Implicit Derivation/Implicit referrals ' + str(cluster) + '.csv'
    writer = open(file, 'w')
    writer.write('PATIENT;MEDICO->MEDICO;MEDICO->ENFERMERA;MEDICO->NUTRICIONISTA;ENFERMERA->MEDICO;ENFERMERA->ENFERMERA;ENFERMERA->NUTRICIONISTA;NUTRICIONISTA->MEDICO;NUTRICIONISTA->ENFERMERA;NUTRICIONISTA->NUTRICIONISTA\n')
    for k in implicit_referrals_per_patient:
        writer.write(str(k) + ';' + str(implicit_referrals_per_patient[k][('MEDICO', 'MEDICO')]) + ';' + str(implicit_referrals_per_patient[k][('MEDICO', 'ENFERMERA')]) + ';'+ str(implicit_referrals_per_patient[k][('MEDICO', 'NUTRICIONISTA')]) + ';'+ str(implicit_referrals_per_patient[k][('ENFERMERA', 'MEDICO')]) + ';'+ str(implicit_referrals_per_patient[k][('ENFERMERA', 'ENFERMERA')]) + ';'+ str(implicit_referrals_per_patient[k][('ENFERMERA', 'NUTRICIONISTA')]) + ';'+ str(implicit_referrals_per_patient[k][('NUTRICIONISTA', 'MEDICO')]) + ';'+ str(implicit_referrals_per_patient[k][('NUTRICIONISTA', 'ENFERMERA')]) + ';'+ str(implicit_referrals_per_patient[k][('NUTRICIONISTA', 'NUTRICIONISTA')]) + '\n')

    writer.close()

    file = 'Reports/Statistics/ID_Resource_Statistics' + str(cluster) + '.txt'
    writer = open(file, 'w')
    writer.write('(nodo1, nodo2): (veces/paciente, frecuencia)\n')
    for k in statistic_dic:
        writer.write(str(k) + ': ')
        for i in statistic_dic[k]:
            writer.write('(' + str(i) + ',' + str(statistic_dic[k][i]) + ') ')
        writer.write('\n')

    writer.close()
    return relations, referrals, statistic_dic


def derivation_executor(events_list):
    relations = {}
    referrals = {}

    for events in events_list:
        for i in range(len(events)-1):
            previous = ''
            for j in range(len(events)-i-1):
                # until the time window defined by events_list or until the professional is repeated
                if events[i].executor == events[i+j+1].executor:
                    break

                # referrals related to 'SALAS DE PROCEDIMIENTO' are removed
                if events[i].estate == 'SALA DE PROCEDIMIENTOS' or events[i+j+1].estate == 'SALA DE PROCEDIMIENTOS':
                    continue

                # duplicated referred professional are considered once
                if events[i+j+1].executor == previous:
                    continue

                executor_tuple = (events[i].executor, events[i+j+1].executor)
                previous = events[i+j+1].executor
                if executor_tuple not in relations:
                    relations[executor_tuple] = 0
                relations[executor_tuple] += 1

                executor = events[i].executor
                #if executor in Reader.estate_professionals['ADMINISTRADOR'] \
                #        or executor in Reader.estate_professionals['ADMINISTRATIVO'] \
                #        or executor in Reader.estate_professionals['SALA DE PROCEDIMIENTOS']:
                #    continue
                if events[i].executor not in referrals:
                    referrals[events[i].executor] = 0
                referrals[events[i].executor] += 1

    return relations, referrals


# Returns the number of days between two dates
def days_between(date1, date2):
    return abs((date2 - date1).days)


# Returns the number of days between two dates
def hours_between(date1, date2):
    return int(abs((date1, date2).total_seconds)/3600)


def professional_freq(cluster):
    return Reader.professional_freq[cluster].copy()


def estate_freq(cluster):
    return Reader.estate_freq[cluster].copy()


def activity_freq(cluster):
    return Reader.act_freq[cluster].copy()


def estate_professionals(cluster):
    return Reader.estate_professionals[cluster].copy()


def next_appointment_cluster(cluster):
    return  Reader.next_appointment[cluster].copy()

def patients_in_cluster(cluster):
    return Reader.cluster_patients[cluster]

def professional_label_cluster(cluster):
    return Reader.professional_number_in_patient[cluster].copy()

# Key: number of professionals that treat a patient. Value: percentage of patients treated by that number
# (for a specific cluster)
def people_per_patient(cluster):
    patient_professionals = Reader.patient_professionals[cluster]
    dic_final = {}
    for patient in patient_professionals:
        size = len(patient_professionals[patient])
        if size not in dic_final:
            dic_final[size] = 0
        dic_final[size] += (float(1)/len(log_patients[cluster]))
    return dic_final


# Key: number of distinct activities per patient. Value: percentage of patients with that number
# (for a specific cluster)
def act_per_patient(cluster):
    patient_activities = Reader.patient_activities[cluster]
    dic_final = {}
    for patient in patient_activities:
        size = len(patient_activities[patient])
        if size not in dic_final:
            dic_final[size] = 0
        dic_final[size] += (float(1)/len(log_patients[cluster]))
    return dic_final


# hba1c measurements
def show_compensation_graph(cluster):
    measurement_of_patients = {}
    reader = open('Log/Compensation Log/marks_' + cluster + '.txt', 'r')
    for mark in reader:
        if mark != '':
            aux_list = mark.strip().split(';')
            measurement_of_patients[aux_list[0]] = [aux_list[1][1:len(aux_list[1])-1].split(','),
                                                    aux_list[2][1:len(aux_list[2])-1].split(',')]
    list_to_graph = {}
    for patient in log_patients[cluster]:
        if patient not in list_to_graph and patient in measurement_of_patients:
            list_to_graph[patient] = measurement_of_patients[patient]

    print(list_to_graph)
    Statistics.graph(list_to_graph, len(list_to_graph))
    reader.close()

#####################################################################################################################
# Function: show_implicit_derivation                                                                                #
# calls a method to draw the graph, returns a node list, a dictionary (relations) of edges used for the drawing,    #
# a dictionary (statistics) with KEY: a tuple (A,B) and VALUE: a list of tuples (N,K) that indicates the relation   #
# B immediately after A happened N times per patient with a frequency of K in all log                               #
# mode: 0 = Activities, 1 = Professionals, 2 = Roles                                                                #
#                                                                                                                   #
#####################################################################################################################
def show_implicit_derivation(cluster, time, mode, relation_threshold, referral_threshold, node_frequency_filter, edge_frequency_filter, info, rel_freq_mode,
                             most_freq):
    nodes = None
    relations = None
    statistics = None
    global times
    events_list = inactivity_identification(cluster, time)
    if mode == 0:
        relations, referrals, inbound, outgoing, statistics = derivation(cluster, events_list)
        nodes, relations = Gr.show_implicit_derivation(cluster, relations, activity_freq(cluster), referrals,
                                                       len(log_patients[cluster]), relation_threshold, time, referral_threshold, node_frequency_filter,
                                                       edge_frequency_filter, less_info=info, most_freq_filter=most_freq)
        # if rel_freq_mode:
        #    Gr.graphicRelationFrequency(inbound, outgoing, Reader.act_freq.keys())
    elif mode == 1:
        relations, referrals = derivation_executor(events_list)
        nodes, relations = Gr.show_implicit_derivation_role(cluster, relations, professional_freq(cluster), referrals,
                                                            estate_professionals(cluster), len(log_patients[cluster]),
                                                            relation_threshold, time, referral_threshold, node_frequency_filter,
                                                            edge_frequency_filter, less_info=info)
    elif mode == 2:
        relations, referrals, statistics = derivation_estate(cluster, events_list)
        nodes, relations = Gr.show_implicit_derivation_role(cluster, relations, estate_freq(cluster), referrals,
                                                            estate_professionals(cluster), len(log_patients[cluster]),
                                                            relation_threshold, time, referral_threshold, node_frequency_filter,
                                                            edge_frequency_filter, less_info=info)

    for i in nodes.keys():
        nodes[i] = float(nodes[i]) / len(log_patients[cluster])
    for i in relations.keys():
        relations[i] = float(relations[i]) / len(log_patients[cluster])

    # times += 1
    return nodes, relations, statistics, len(log_patients[cluster])


#####################################################################################################################
# Function: show_duo                                                                                                #
# calls a method to do the graph drawing, computes the DUO relation. Returns a list of nodes and a dictionary of    #
# edges used for the drawing                                                                                        #
#                                                                                                                   #
#                                                                                                                   #
#                                                                                                                   #
#####################################################################################################################
def show_duo(cluster, time, relation_threshold, node_frequency_filter, edge_frequency_filter, info):
    global times
    event_list = inactivity_identification(cluster, time)
    relations = {}

    for events in event_list:
        estate = 0
        while estate < (len(events) - 1):
            personal_duo = []
            for j in range(1, len(events)-estate):
                if events[estate].act == 'DUPLA' == events[estate+j].act \
                        and events[estate].executor != events[estate+j].executor \
                        and events[estate].time == events[estate+j].time:
                    if j == 1:
                        personal_duo.append(events[estate].estate)
                    personal_duo.append(events[estate+j].estate)
                else:
                    break

            estate_tuple = set()
            for j in range(0, len(personal_duo)):
                estate_tuple = estate_tuple | personal_duo[j]
            estate_tuple = tuple(estate_tuple)

            if estate_tuple not in relations:
                relations[estate_tuple] = 0
            relations[estate_tuple] += 1

            estate += 1

    sorted_relations = sorted(relations.items(), key=operator.itemgetter(1))

    estate_frequency = estate_freq(cluster)
    remove_keys = []
    #Do the pre-processing
    for estate in estate_frequency:
        if estate_frequency[estate] < node_frequency_filter:
            remove_keys.append(estate)

    for keys in remove_keys:
            del estate_frequency[keys]
    #Writing reports
    file = 'Reports/Duo_relation_frequency' + str(cluster) + '.txt'
    writer = open(file, 'w')
    for relation in sorted_relations:
        if len(relation[0]) == 2: #two professionals related
            if relation[0][0] not in estate_frequency or relation[0][1] not in estate_frequency:
                del relations[(str(relation[0][0]),str(relation[0][1]))]
                if info:
                    continue
            elif relation[1] < edge_frequency_filter:
                del relations[(str(relation[0][0]),str(relation[0][1]))]
                if info:
                    continue
            writer.write(str(relation[0][0]) + '->' + str(relation[0][1]) + ':' + str(relation[1]) + '\n')

        elif len(relation[0]) == 3: #three professionals related
            if relation[0][0][:len(relation[0][0])-1] not in estate_frequency or relation[0][1][:len(relation[0][1])-1] not in estate_frequency or relation[0][2][:len(relation[0][2])-1] not in estate_frequency:
                del relations[(str(relation[0][0]),str(relation[0][1]),str(relation[0][2]))]
                if info:
                    continue
            elif relation[1] < edge_frequency_filter:
                del relations[(str(relation[0][0]),str(relation[0][1]),str(relation[0][2]))]
                if info:
                    continue
            writer.write(str(relation[0][0][:len(relation[0][0])-1]) + '<->' + str(relation[0][1][:len(relation[0][1])-1]) + '<->' + str(relation[0][2][:len(relation[0][2])-1]) + ':' + str(relation[1]) + '\n')
        elif len(relation[0]) == 4: #four professionals related
            if relation[0][0][:len(relation[0][0])-2] not in estate_frequency or relation[0][1][:len(relation[0][1])-2] not in estate_frequency or relation[0][2][:len(relation[0][2])-2] not in estate_frequency or relation[0][3][:len(relation[0][3])-2] not in estate_frequency:
                del relations[(str(relation[0][0]),str(relation[0][1]),str(relation[0][2]),str(relation[0][3]))]
                if info:
                    continue
            elif relation[1] < edge_frequency_filter:
                del relations[(str(relation[0][0]),str(relation[0][1]),str(relation[0][2]),str(relation[0][3]))]
                if info:
                    continue
            writer.write(str(relation[0][0][:len(relation[0][0])-2]) + '<->' + str(relation[0][1][:len(relation[0][1])-2]) + '<->' + str(relation[0][2][:len(relation[0][2])-2]) + '<->' + str(relation[0][3][:len(relation[0][3])-2]) +  ':' + str(relation[1]) + '\n')
    writer.write('\n\nSum: ' + str(np.sum(list(relations.values())))+'\nMean: ' + str(round(np.mean(list(relations.values())),3)) + '\nSD: ' + str(round(np.std(list(relations.values())),3))+ '\nCases: '+ str(len(Reader.patient_cluster)))
    writer.close()
    times += 1

    #Method that draws the graph
    nodes, b = Gr.showDuo(cluster, relations, estate_frequency, estate_professionals(cluster), relation_threshold, node_frequency_filter, edge_frequency_filter, time)

    #normalize dictionaries by #patients
    for estate in nodes.keys():
        nodes[estate] = float(nodes[estate]) / len(Reader.patients)
    for estate in relations.keys():
        relations[estate] = float(relations[estate]) / len(Reader.patients)
    return nodes, relations


#####################################################################################################################
# Function: show_explicit_derivation                                                                                #
# calls a method to do the graph drawing, computes the EXPLICIT DERIVATION relation. Returns a list of nodes and a  #
# dictionary of edges used for the drawing                                                                          #
#                                                                                                                   #
#                                                                                                                   #
#                                                                                                                   #
#####################################################################################################################
def show_explicit_derivation(cluster, time, threshold, professional_labeled_threshold, node_frequency_filter, absolute_freq_filter, relative_freq_filter, info, date_start, date_finish):
    global times
    years = date_finish[1] - date_start[1]+ 1
    event_list = sorted(log_patients[cluster].items(), key=operator.itemgetter(0))
    referrals_between_estates_withfail = {}
    min_max_dates = {}
    referrals_between_estates = {}
    referrals_between_labeled_estates = {}
    appointment_derivation = next_appointment_cluster(cluster)
    professionals_labeled = professional_label_cluster(cluster)
    reader = open('Input/Explicit_Derivation.txt', 'r')
    valid_acts = []
    valid_estates = []
    same_estate_constraint = True

    if date_finish[0] in [1,3,5,7,8,10,12]:
        referral_deadline = datetime(date_finish[1], date_finish[0], 31).date()
    elif date_finish[0] in [4,6,9,11]:
        referral_deadline = datetime(date_finish[1], date_finish[0], 30).date()
    else:
        referral_deadline = datetime(date_finish[1], date_finish[0], 28).date()
    for line in reader:
        valid_acts.append(line.strip())
    reader.close()

    reader = open('Input/ED_estates.txt', 'r')
    for line in reader:
        valid_estates.append(line.strip())
    reader.close()

    periods_between_appointments = {}

    # dictionaries with statistic data
    effective_referral = {}
    total_referral = {}
    effective_referral_detailed = {}
    total_referral_detailed = {}

    #Key: patient. Value: dict with key: period and value: total derivations
    patient_period_explicit_derivations = Reader.patient_period_derivations

    #Key: patient. Value: dict with key: period and value: effective derivations
    patient_period_adherence = {}

    med_med = {}
    med_enf = {}
    med_nut = {}
    med_med_fail = {}
    med_enf_fail = {}
    med_nut_fail = {}
    enf_med = {}
    enf_enf = {}
    enf_nut = {}
    enf_med_fail = {}
    enf_enf_fail = {}
    enf_nut_fail = {}
    nut_med = {}
    nut_enf = {}
    nut_nut = {}
    nut_med_fail = {}
    nut_enf_fail = {}
    nut_nut_fail = {}

    tuple_relation_list = [('MEDICO', 'MEDICO'), ('MEDICO', 'ENFERMERA'), ('MEDICO', 'NUTRICIONISTA'), ('ENFERMERA', 'MEDICO'), ('ENFERMERA', 'ENFERMERA'), ('ENFERMERA', 'NUTRICIONISTA'), ('NUTRICIONISTA', 'MEDICO'), ('NUTRICIONISTA', 'ENFERMERA'), ('NUTRICIONISTA', 'NUTRICIONISTA')]

    for start_tuple in tuple_relation_list:
        referrals_between_estates_withfail[start_tuple] = 0

    for patient in log_patients[cluster]:
        total_referral[patient] = 0
        effective_referral[patient] = 0
        total_referral_detailed[int(patient)] = {}
        effective_referral_detailed[int(patient)] = {}
        patient_period_adherence[patient] = {}
        total_referral_detailed[int(patient)][('MEDICO', 'MEDICO')] = 0
        total_referral_detailed[int(patient)][('MEDICO', 'ENFERMERA')] = 0
        total_referral_detailed[int(patient)][('MEDICO', 'NUTRICIONISTA')] = 0
        total_referral_detailed[int(patient)][('ENFERMERA', 'MEDICO')] = 0
        total_referral_detailed[int(patient)][('ENFERMERA', 'ENFERMERA')] = 0
        total_referral_detailed[int(patient)][('ENFERMERA', 'NUTRICIONISTA')] = 0
        total_referral_detailed[int(patient)][('NUTRICIONISTA', 'MEDICO')] = 0
        total_referral_detailed[int(patient)][('NUTRICIONISTA', 'ENFERMERA')] = 0
        total_referral_detailed[int(patient)][('NUTRICIONISTA', 'NUTRICIONISTA')] = 0
        effective_referral_detailed[int(patient)][('MEDICO', 'MEDICO')] = 0
        effective_referral_detailed[int(patient)][('MEDICO', 'ENFERMERA')] = 0
        effective_referral_detailed[int(patient)][('MEDICO', 'NUTRICIONISTA')] = 0
        effective_referral_detailed[int(patient)][('ENFERMERA', 'MEDICO')] = 0
        effective_referral_detailed[int(patient)][('ENFERMERA', 'ENFERMERA')] = 0
        effective_referral_detailed[int(patient)][('ENFERMERA', 'NUTRICIONISTA')] = 0
        effective_referral_detailed[int(patient)][('NUTRICIONISTA', 'MEDICO')] = 0
        effective_referral_detailed[int(patient)][('NUTRICIONISTA', 'ENFERMERA')] = 0
        effective_referral_detailed[int(patient)][('NUTRICIONISTA', 'NUTRICIONISTA')] = 0
        med_med[patient] = 0
        med_enf[patient] = 0
        med_nut[patient] = 0
        med_med_fail[patient] = 0
        med_enf_fail[patient] = 0
        med_nut_fail[patient] = 0
        enf_med[patient] = 0
        enf_enf[patient] = 0
        enf_nut[patient] = 0
        enf_med_fail[patient] = 0
        enf_enf_fail[patient] = 0
        enf_nut_fail[patient] = 0
        nut_med[patient] = 0
        nut_enf[patient] = 0
        nut_nut[patient] = 0
        nut_med_fail[patient] = 0
        nut_enf_fail[patient] = 0
        nut_nut_fail[patient] = 0
        min_max_dates[patient] = [10000, -1]

    print(len(event_list), len(appointment_derivation))

    for events in event_list:
        patient_case = events[0]

        if int(patient_case) not in appointment_derivation:
            #print ('no se encontro '+ str(patient_case) + ' en el cubo en la fecha indicada')
            continue

        for derivation in appointment_derivation[int(patient_case)]:
            conditional_derivation = False
            if derivation[1] == 'ANY':
                continue
            cube_appoint_date = derivation[0].date()
            if cube_appoint_date.month > int(derivation[2]):
                cube_years = cube_appoint_date.year + 1
            else:
                cube_years = cube_appoint_date.year
            if int(derivation[2]) in [1,3,5,7,8,10,12]:
                cube_limit_date = datetime(cube_years, int(derivation[2]), 31).date()
            elif int(derivation[2]) in [4,6,9,11]:
                cube_limit_date = datetime(cube_years, int(derivation[2]), 30).date()
            else:
                cube_limit_date = datetime(cube_years, int(derivation[2]), 28).date()

            if cube_limit_date - timedelta(days = time) <= cube_appoint_date:
                cube_start_date = cube_appoint_date + timedelta(days = 1)

            else:
                cube_start_date = cube_limit_date - timedelta(days = time)

            if cube_limit_date + timedelta(days = time) > referral_deadline and cube_limit_date <= referral_deadline:
                cube_limit_date = referral_deadline
                conditional_derivation = True
            elif cube_limit_date + timedelta(days = time) <= referral_deadline:
                cube_limit_date = cube_limit_date + timedelta(days = time)
            elif cube_limit_date > referral_deadline:
                #print(patient_case, 'continuamos', cube_limit_date)
                continue 
            else:
                print('malo jiji')

            for i in range(len(events[1])):
                current_appoint_date = events[1][i].time.date()
                if current_appoint_date.year == cube_appoint_date.year and current_appoint_date.month == cube_appoint_date.month and current_appoint_date.day == cube_appoint_date.day  and (events[1][i].act in valid_acts) and (events[1][i].estate in valid_estates):
                    if i+1 == len(events[1]):
                        if derivation[1] == 'MEDICO' or derivation[1] == 'GRUPAL MEDICO':
                            estate1 = 'MED_FAIL'
                            estate2 = 'MEDICO'
                        if derivation[1] == 'ENFERMERA' or derivation[1] == 'GRUPAL ENFERMERA':
                            estate1 = 'ENF_FAIL'
                            estate2 = 'ENFERMERA'
                        if derivation[1] == 'NUTRICIONISTA' or derivation[1] == 'GRUPAL NUTRICIONISTA':
                            estate1 = 'NUT_FAIL'
                            estate2 = 'NUTRICIONISTA'
                        tuplex = (events[1][i].estate, estate1)
                        tuple2 = (events[1][i].estate, estate2)
                        tuple_avg_time = (events[1][i].estate, estate2, patient_case)
                        total_referral[events[1][i].patient] += 1
                        total_referral_detailed[patient_case][tuple2] += 1
                        if tuplex not in referrals_between_estates_withfail:
                            referrals_between_estates_withfail[tuplex] = 0
                        referrals_between_estates_withfail[tuplex] += 1
                        
                        timex = (events[1][i].time.year - 2012)*12 + events[1][i].time.month
                        if timex < min_max_dates[patient_case][0]:
                            min_max_dates[patient_case][0] = timex
                        if timex > min_max_dates[patient_case][1]:
                            min_max_dates[patient_case][1] = timex

                        if tuple2 not in referrals_between_estates:
                            referrals_between_estates[tuple2] = 0
                        if tuple_avg_time not in periods_between_appointments:
                            periods_between_appointments[tuple_avg_time] = []
                        days_between_attentions = (cube_limit_date - timedelta(days = time) - current_appoint_date).days
                        periods_between_appointments[tuple_avg_time].append(float(days_between_attentions)/30)
                        referrals_between_estates[tuple2] += 1
                    else:
                        found = False
                        for j in range(i+1, len(events[1])):
                            if not (events[1][i].estate in valid_estates) or not (events[1][j].estate in valid_estates) or not (events[1][j].act in valid_acts):
                                continue
                            next_appoint_date = events[1][j].time.date()
                            if derivation[1] == 'MEDICO' or derivation[1] == 'GRUPAL MEDICO':
                                estate1 = 'MED_FAIL'
                                estate2 = 'MEDICO'
                            if derivation[1] == 'ENFERMERA' or derivation[1] == 'GRUPAL ENFERMERA':
                                estate1 = 'ENF_FAIL'
                                estate2 = 'ENFERMERA'
                            if derivation[1] == 'NUTRICIONISTA' or derivation[1] == 'GRUPAL NUTRICIONISTA':
                                estate1 = 'NUT_FAIL'
                                estate2 = 'NUTRICIONISTA'
                            
                            if (cube_start_date <= next_appoint_date <= cube_limit_date) and (events[1][j].estate == estate2 or not same_estate_constraint):
                        
                                tuplex = (events[1][i].estate, events[1][j].estate)
                                
                                tuple_avg_time = (events[1][i].estate, events[1][j].estate, patient_case)

                                #detailed_tuple = (professionals_labeled[str(patient_case)][events[1][i].executor], professionals_labeled[str(patient_case)][events[1][j].executor])
                                detailed_tuple = ("NO INFO", "NO INFO")
                                
                                found = True
                                if tuplex not in referrals_between_estates_withfail:
                                    referrals_between_estates_withfail[tuplex] = 0
                                referrals_between_estates_withfail[tuplex] += 1

                                timex = (events[1][i].time.year - 2012)*12 + events[1][i].time.month
                                if timex < min_max_dates[patient_case][0]:
                                    min_max_dates[patient_case][0] = timex
                                if timex > min_max_dates[patient_case][1]:
                                    min_max_dates[patient_case][1] = timex

                                if tuplex not in referrals_between_estates:
                                    referrals_between_estates[tuplex] = 0
                                if tuple_avg_time not in periods_between_appointments:
                                    periods_between_appointments[tuple_avg_time] = []
                                if detailed_tuple not in referrals_between_labeled_estates:
                                    referrals_between_labeled_estates[detailed_tuple] = 0
                                referrals_between_labeled_estates[detailed_tuple] += 1
                                days_between_attentions = (next_appoint_date - current_appoint_date).days
                                periods_between_appointments[tuple_avg_time].append(float(days_between_attentions)/30)
                                referrals_between_estates[tuplex] += 1
                                total_referral[events[1][i].patient] += 1
                                effective_referral[events[1][i].patient] += 1

                                total_referral_detailed[patient_case][tuplex] += 1
                                effective_referral_detailed[patient_case][tuplex] += 1


                                if events[1][i].act == events[1][j].act == 'CONTROL CV MEDICO':
                                    med_med[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV MEDICO' and events[1][j].act == 'CONTROL CV ENFERMERA':
                                    med_enf[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV MEDICO' and events[1][j].act == 'CONTROL CV NUTRICIONISTA':
                                    med_nut[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV ENFERMERA' and events[1][j].act == 'CONTROL CV MEDICO':
                                    enf_med[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV ENFERMERA' and events[1][j].act == 'CONTROL CV ENFERMERA':
                                    enf_enf[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV ENFERMERA' and events[1][j].act == 'CONTROL CV NUTRICIONISTA':
                                    enf_nut[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV NUTRICIONISTA' and events[1][j].act == 'CONTROL CV MEDICO':
                                    nut_med[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV NUTRICIONISTA' and events[1][j].act == 'CONTROL CV ENFERMERA':
                                    nut_enf[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV NUTRICIONISTA' and events[1][j].act == 'CONTROL CV NUTRICIONISTA':
                                    nut_nut[events[1][i].patient] += 1

                                break

                            if next_appoint_date > cube_limit_date:
                                if conditional_derivation:
                                    break

                                found = True

                                tuplex = (events[1][i].estate, estate1)
                                tuple2 = (events[1][i].estate, estate2)
                                tuple_avg_time = (events[1][i].estate, estate2, patient_case)
                                total_referral[events[1][i].patient] += 1

                                total_referral_detailed[patient_case][tuple2] += 1

                                if tuplex not in referrals_between_estates_withfail:
                                    referrals_between_estates_withfail[tuplex] = 0
                                referrals_between_estates_withfail[tuplex] += 1

                                timex = (events[1][i].time.year - 2012)*12 + events[1][i].time.month
                                if timex < min_max_dates[patient_case][0]:
                                    min_max_dates[patient_case][0] = timex
                                if timex > min_max_dates[patient_case][1]:
                                    min_max_dates[patient_case][1] = timex

                                if tuple2 not in referrals_between_estates:
                                    referrals_between_estates[tuple2] = 0
                                if tuple_avg_time not in periods_between_appointments:
                                    periods_between_appointments[tuple_avg_time] = []
                                days_between_attentions = (cube_limit_date - timedelta(days = time) - current_appoint_date).days
                                periods_between_appointments[tuple_avg_time].append(float(days_between_attentions)/30)

                                referrals_between_estates[tuple2] += 1

                                if events[1][i].act == 'CONTROL CV MEDICO' and estate1 == 'MED_FAIL' :
                                    med_med_fail[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV MEDICO' and estate1 == 'ENF_FAIL':
                                    med_enf_fail[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV MEDICO' and estate1 == 'NUT_FAIL':
                                    med_nut_fail[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV ENFERMERA' and estate1 == 'MED_FAIL':
                                    enf_med_fail[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV ENFERMERA' and estate1 == 'ENF_FAIL':
                                    enf_enf_fail[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV ENFERMERA' and estate1 == 'NUT_FAIL':
                                    enf_nut_fail[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV NUTRICIONISTA' and estate1 == 'MED_FAIL':
                                    nut_med_fail[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV NUTRICIONISTA' and estate1 == 'ENF_FAIL':
                                    nut_enf_fail[events[1][i].patient] += 1
                                if events[1][i].act == 'CONTROL CV NUTRICIONISTA' and estate1 == 'NUT_FAIL':
                                    nut_nut_fail[events[1][i].patient] += 1
                                break

                        if not found:
                            if events[1][-1].time.date() <= cube_limit_date:
                                continue
                            if derivation[1] == 'MEDICO' or derivation[1] == 'GRUPAL MEDICO':
                                estate1 = 'MED_FAIL'
                                estate2 = 'MEDICO'
                            if derivation[1] == 'ENFERMERA' or derivation[1] == 'GRUPAL ENFERMERA':
                                estate1 = 'ENF_FAIL'
                                estate2 = 'ENFERMERA'
                            if derivation[1] == 'NUTRICIONISTA' or derivation[1] == 'GRUPAL NUTRICIONISTA':
                                estate1 = 'NUT_FAIL'
                                estate2 = 'NUTRICIONISTA'

                            tuplex = (events[1][i].estate, estate1)
                            tuple2 = (events[1][i].estate, estate2)
                            tuple_avg_time = (events[1][i].estate, estate2, patient_case)
                            total_referral[events[1][i].patient] += 1

                            total_referral_detailed[patient_case][tuple2] += 1

                            if tuplex not in referrals_between_estates_withfail:
                                referrals_between_estates_withfail[tuplex] = 0
                            referrals_between_estates_withfail[tuplex] += 1

                            timex = (events[1][i].time.year - 2012)*12 + events[1][i].time.month
                            if timex < min_max_dates[patient_case][0]:
                                min_max_dates[patient_case][0] = timex
                            if timex > min_max_dates[patient_case][1]:
                                min_max_dates[patient_case][1] = timex

                            if tuple2 not in referrals_between_estates:
                                referrals_between_estates[tuple2] = 0
                            if tuple_avg_time not in periods_between_appointments:
                                periods_between_appointments[tuple_avg_time] = []
                            days_between_attentions = (cube_limit_date - timedelta(days = time) - current_appoint_date).days
                            periods_between_appointments[tuple_avg_time].append(float(days_between_attentions)/30)

                            referrals_between_estates[tuple2] += 1


    annual_appointment = {}
    #print(total_referral_detailed)
    for k in periods_between_appointments:
        relation_tuple = (k[0],k[1])
        if relation_tuple not in annual_appointment:
            annual_appointment[relation_tuple] = []
        asdasd = round(float(12*len(periods_between_appointments[k]))/((np.sum(list(periods_between_appointments[k])))*len(professionals_labeled)),3)

        annual_appointment[relation_tuple].append(asdasd)

    daux = sorted(referrals_between_estates_withfail.items(), key=operator.itemgetter(1))
    sorted_referrals_between_estates = sorted(referrals_between_estates.items(), key=operator.itemgetter(1))
    sorted_annual_appointment = sorted(annual_appointment.items(), key=operator.itemgetter(1))
    num_of_derivations = np.sum(list(referrals_between_estates.values())) 

    if same_estate_constraint:
        same_estate_constraint = 'R'
    else:
        same_estate_constraint = 'F'

    average_annual_appoint = {}

    file = 'Reports/Explicit Derivation/Norm derivation ' + str(same_estate_constraint) + ' ' + str(cluster) + '.csv'
    writer = open(file, 'w')
    writer.write('PATIENT;')
    for tuplexx in tuple_relation_list:
        writer.write('NORM ' + str(tuplexx) + ';')
        average_annual_appoint[tuplexx] = []
    writer.write('\n')
    for k in list(total_referral.keys()):
        treatment_months = min_max_dates[k][1] - min_max_dates[k][0] + 1
        if treatment_months < 6:
            continue
        writer.write(str(k) + ";")
        for i in range(len(tuple_relation_list)):
            res = round(total_referral_detailed[k][tuple_relation_list[i]]*12/treatment_months, 3)
            writer.write(str(res))
            if res > 0.001:
                average_annual_appoint[tuple_relation_list[i]].append(res)
            if i < len(tuple_relation_list) - 1:
                writer.write(';')
        writer.write('\n')
    writer.close()

    file = 'Reports/Explicit Derivation/Nuevos Clusters/PA ' + str(same_estate_constraint) + ' ' + str(cluster) + '.csv'
    writer = open(file, 'w')
    writer.write('PATIENT;EFFECTIVE;TOTAL;PERCENTAGE\n')
    for k in list(total_referral.keys()):
        if total_referral[k] == 0:
            del total_referral[k]
            del effective_referral[k]
        else:
            writer.write(str(k) + ';' + str(effective_referral[k]) + ';' + str(total_referral[k]) + ';' + str(round(effective_referral[k]/total_referral[k], 2)) + '\n')
    writer.close()

    file = 'Reports/Explicit Derivation/Nuevos Clusters/PAD ' + str(same_estate_constraint) + ' ' + str(cluster) + '.csv'
    writer = open(file, 'w')
    writer.write('PATIENT;')
    for tuplex in tuple_relation_list:
        writer.write('EFFECTIVE ' + str(tuplex) + ';TOTAL ' + str(tuplex) + ';')
    writer.write('\n')
    for k in list(total_referral.keys()):
        writer.write(str(k) + ';')
        for i in range(len(tuple_relation_list)):
            writer.write(str(effective_referral_detailed[k][tuple_relation_list[i]]) + ';' + str(total_referral_detailed[k][tuple_relation_list[i]]))
            if i < len(tuple_relation_list) - 1:
                writer.write(';')
        writer.write('\n')
    writer.close()

    file = 'Reports/Explicit Derivation/ED_relation_frequency_detailed ' + str(cluster) + '.txt'
    writer = open(file, 'w')
    for i in daux:
        if i[1] < relative_freq_filter:
            del referrals_between_estates_withfail[(str(i[0][0]),str(i[0][1]))]
            if info:
                continue
        writer.write(str(i[0][0]) + '->' + str(i[0][1]) + ':' + str(i[1]) + '\n')
    writer.write('\n\nSum: ' + str(np.sum(list(referrals_between_estates_withfail.values())))+'\nMean: ' + str(round(np.mean(list(referrals_between_estates_withfail.values())),3)) + '\nSD: ' + str(round(np.std(list(referrals_between_estates_withfail.values())),3)) + '\nCases: ' + str(len(total_referral)))
    writer.close()

    file = 'Reports/Explicit Derivation/ED Relation ' + str(same_estate_constraint) + ' ' + str(cluster) + '.csv'
    writer = open(file, 'w')
    writer.write('FROM;TO;FREQUENCY\n')
    print (sorted_referrals_between_estates)
    for i in sorted_referrals_between_estates:
        if float(i[1])/num_of_derivations < relative_freq_filter:
            del referrals_between_estates[(str(i[0][0]),str(i[0][1]))]
            del referrals_between_estates_withfail[(str(i[0][0]),str(i[0][1]))]
            del referrals_between_estates_withfail[(str(i[0][0]),str(i[0][1])[0:3] + '_FAIL')]
            if info:
                continue
        elif float(i[1]) < absolute_freq_filter:
            del referrals_between_estates[(str(i[0][0]),str(i[0][1]))]
            del referrals_between_estates_withfail[(str(i[0][0]),str(i[0][1]))]
            del referrals_between_estates_withfail[(str(i[0][0]),str(i[0][1])[0:3] + '_FAIL')]
            if info:
                continue
        writer.write(str(i[0][0]) + ';' + str(i[0][1]) + ';' + str(i[1]) + '\n')
    writer.write('\n\nSum: ' + str(np.sum(list(referrals_between_estates.values())))+'\nMean: ' + str(round(np.mean(list(referrals_between_estates.values())),3)) + '\nSD: ' + str(round(np.std(list(referrals_between_estates.values())),3)) + '\nCases: ' + str(len(total_referral)))
    writer.close()

    file = 'Reports/Explicit Derivation/Annual_relation_frequency_list' + str(times) + '.txt'
    writer = open(file, 'w')
    for i in sorted_annual_appointment:
        relation_mean = round(np.mean(list(i[1])),3)
        if  relation_mean< absolute_freq_filter:
            del annual_appointment[(str(i[0][0]),str(i[0][1]))]
            if info:
                continue
        writer.write(str(i[0][0]) + '->' + str(i[0][1]) + ':' + str(i[1]) + '\n')
    #writer.write('\n\nSum: ' + str(np.sum(list(annual_appointment.values())))+'\nMean: ' + str(round(np.mean(list(annual_appointment.values())),3)) + '\nSD: ' + str(round(np.std(list(annual_appointment.values())),3)) + '\nCases: ' + str(len(total_referral)))
    writer.close()

    role_list = estate_freq(cluster)
    raux = sorted(role_list.items(), key=operator.itemgetter(1))

    file = 'Reports/Explicit Derivation/Resource_frequency'  + str(times) + '.txt'
    writer = open(file, 'w')
    for i in raux:
        if role_list[str(i[0])] < node_frequency_filter or i[0] not in ['MEDICO', 'ENFERMERA', 'NUTRICIONISTA']:
            del role_list[str(i[0])]
            if info:
                continue
        writer.write(str(i[0]) + ':' + str(i[1]) + '\n')
    writer.write('\n\nSum: ' + str(np.sum(list(role_list.values())))+'\nMean: ' + str(round(np.mean(list(role_list.values())),3)) + '\nSD: ' + str(round(np.std(list(role_list.values())),3))+ '\nCases: ' + str(len(total_referral)))
    writer.close()
    times += 1

    #periods_between_appointments

    #professional_labeled_threshold = 0.05
    #Gr.showExplicitDerivation(cluster, referrals_between_estates, average_annual_appoint, referrals_between_estates_withfail, referrals_between_labeled_estates, role_list, threshold, professional_labeled_threshold, node_frequency_filter, relative_freq_filter, absolute_freq_filter, time, len(total_referral))

    for i in role_list.keys():
        role_list[i] = float(role_list[i]) / len(total_referral)
    for i in referrals_between_estates_withfail.keys():
        referrals_between_estates_withfail[i] = float(referrals_between_estates_withfail[i]) / len(total_referral)

    return role_list, referrals_between_estates, referrals_between_estates_withfail, effective_referral, total_referral, average_annual_appoint

#def compareImplicit(filename1, filename2, node1, relation1, node2, relation2, statisticA, statisticB, patientsA, patientsB, node_threshold, rel_threshold):
    #relaciones_significativas = Statistics.statistic_hist(statisticA, statisticB, patientsA, patientsB, filename1[4:], filename2[4:])
    #Gr.showLogContrast(node1, relation1, node2, relation2, node_threshold, rel_threshold, role_groups(), relaciones_significativas)

def compareExplicit(node1, relation1, annualavg1, node2, relation2, annualavg2, node_threshold, relative_threshold, absolute_threshold):
    #Gr.showLogContrast(node1, relation1, node2, relation2, node_threshold, rel_threshold, role_groups(), [], filter = False)
    Gr.showExplicitContrast(node1, relation1, annualavg1, node2, relation2, annualavg2, node_threshold, relative_threshold, absolute_threshold)

def compareAdherenceExplicit(filename1, filename2, successA, totalA, successB, totalB, confidence):
    Statistics.chisq(confidence)
    Statistics.adherence_hist(successA, totalA, successB, totalB, filename1[4:], filename2[4:])

#def compareDuo(filename1, filename2, node1, relation1, node2, relation2, node_threshold, rel_threshold):
    #Gr.showLogContrast(node1, relation1, node2, relation2, node_threshold, rel_threshold, role_groups(), [], filter = False)

def compareData(personDic1, personDic2, actDic1, actDic2, name1, name2):
    Statistics.hist_sample(personDic1, personDic2, name1[4:], name2[4:], 'Professionals per patient', 'frequency')
    Statistics.hist_sample(actDic1, actDic2, name1[4:], name2[4:], 'Activities per patient', 'frequency')

def compareSegmentData(patientDic, name1, name2, num_of_measurements, num_of_segments, compensation_delta):
    statistic_list = []
    for i in range(num_of_segments):
        new_dic = {}
        for j in range(0, 5, compensation_delta):
            new_dic[(j, j+1)] = 0
            new_dic[(j, -(j+1))] = 0
        statistic_list.append(new_dic)
    for patient in patientDic:
        if len(patientDic[patient][0][0]) >= num_of_measurements:
            for k in range(len(patientDic[patient][0][0]) - 1):
                delta = patientDic[patient][0][1][k+1] - patientDic[patient][0][1][k]




def showAll(time, mode, threshold, arrow, frequency, global_freq, info):
    events_list = inactivity_identification(Reader.patients, time)
    relaciones, derivaciones = derivation_estate(events_list)

    event_liscube_appoint_date = sorted(Reader.patients.items(), key=operator.itemgetter(0))
    relations = {}
    derivation_index = 0
    citas = sorted(Reader.next_appointment.items(), key=operator.itemgetter(0))

    reader = open('Input/Explicit_Derivation.txt', 'r')
    lista_buenos = []
    for line in reader:
        lista_buenos.append(line.strip())
    reader.close()

    for events in event_liscube_appoint_date:
        while int(events[0]) > citas[derivation_index][0]:
            derivation_index += 1
        if int(events[0]) < citas[derivation_index][0]:
            print ('no se encontro '+ str(events[0]) + ' en el cubo en la fecha indicada')
            continue
        for derivation in citas[derivation_index][1]:
            for i in range(len(events[1])):
                current_appoint_date = datetime.strptime(events[1][i].time, "%Y/%m/%d %H:%M")
                cube_appoint_date = datetime.strptime(derivation[0], "%Y-%m-%d")
                if current_appoint_date.year == cube_appoint_date.year and current_appoint_date.month == cube_appoint_date.month and current_appoint_date.day == cube_appoint_date.day and events[1][i].estate == derivation[0] and (events[1][i].act in lista_buenos):
                    if int(derivation[3]) - current_appoint_date.month > time//30:
                        if int(derivation[3]) > 9:
                            timestartstring = str(current_appoint_date.year) + '/' + str(int(derivation[3]) - time//30) +'/01'
                        else:
                            timestartstring = str(current_appoint_date.year) + '/0' + str(int(derivation[3]) - time//30) +'/01'
                        inicio = datetime.strptime(timestartstring, "%Y/%m/%d").date()
                        fin = inicio + timedelta(days = time*2)
                    elif int(derivation[3]) - current_appoint_date.month >= 0:
                        if int(current_appoint_date.month) > 9:
                            timestartstring = str(current_appoint_date.year) + '/' + str(current_appoint_date.month) +'/01'
                        else:
                            timestartstring = str(current_appoint_date.year) + '/0' + str(current_appoint_date.month) +'/01'
                        if int(derivation[3]) > 9:
                            timestring = str(current_appoint_date.year) + '/' + str(int(derivation[3])) +'/01'
                        else:
                            timestring = str(current_appoint_date.year) + '/0' + str(int(derivation[3])) +'/01'

                        inicio = datetime.strptime(timestartstring, "%Y/%m/%d").date()
                        fin = datetime.strptime(timestring, "%Y/%m/%d").date()
                        fin = fin + timedelta(days = time)
                    else:
                        if 12 + (int(derivation[3]) - current_appoint_date.month) > time//30:
                            if int(derivation[3]) > 9:
                                timestring = str(current_appoint_date.year + 1) + '/' + str(int(derivation[3])) +'/01'
                            else:
                                timestring = str(current_appoint_date.year + 1) + '/0' + str(int(derivation[3])) +'/01'

                            appoint = datetime.strptime(timestring, "%Y/%m/%d").date()
                            inicio = appoint - timedelta(days = time)
                            fin = appoint + timedelta(days = time)
                        else:
                            if current_appoint_date.month + 1 > 12:
                                timestartstring = str(current_appoint_date.year + 1) + '/01' +'/01'
                                if int(derivation[3]) > 9:
                                    timestring = str(current_appoint_date.year + 1) + '/' + str(int(derivation[3])) +'/01'
                                else:
                                    timestring = str(current_appoint_date.year + 1) + '/0' + str(int(derivation[3])) +'/01'
                                appoint = datetime.strptime(timestring, "%Y/%m/%d").date()
                                inicio = datetime.strptime(timestartstring, "%Y/%m/%d").date()
                                fin = appoint + timedelta(days = time)
                            else:
                                if int(current_appoint_date.month + 1) > 9:
                                    timestartstring = str(current_appoint_date.year) + '/' + str(current_appoint_date.month + 1) +'/01'
                                else:
                                    timestartstring = str(current_appoint_date.year) + '/0' + str(current_appoint_date.month + 1) +'/01'
                                if int(derivation[3]) > 9:
                                    timestring = str(current_appoint_date.year + 1) + '/' + str(int(derivation[3])) +'/01'
                                else:
                                    timestring = str(current_appoint_date.year + 1) + '/0' + str(int(derivation[3])) +'/01'
                                appoint = datetime.strptime(timestring, "%Y/%m/%d").date()
                                inicio = datetime.strptime(timestartstring, "%Y/%m/%d").date()
                                fin = appoint + timedelta(days = time)
                    for j in range(i+1, len(events[1]) - 1):

                        fecha = datetime.strptime(events[1][j].time, "%Y/%m/%d %H:%M").date()
                        if derivation[2] == 'MED' or derivation[2] == 'GRUPAL MED':
                            estate1 = 'MED'
                        if derivation[2] == 'ENF' or derivation[2] == 'GRUPAL ENF':
                            estate1 = 'ENF'
                        if derivation[2] == 'NUTRI' or derivation[2] == 'GRUPAL NUTRI':
                            estate1 = 'NUT'
                        if (inicio <= fecha <= fin) and (events[1][j].act in lista_buenos):
                            tuple = (events[1][i].estate, events[1][j].estate)
                            if tuple not in relations:
                                relations[tuple] = 0
                            relations[tuple] += 1
                            break
                        if fecha > fin:
                            tuple = (events[1][i].estate, estate1)
                            if tuple not in relations:
                                relations[tuple] = 0
                            relations[tuple] += 1
                            break

    daux = sorted(relations.items(), key=operator.itemgetter(1))


    writer= open('Reports/ED_relation_frequency.txt', 'w')
    for i in daux:
        writer.write(str(i[0][0]) + '->' + str(i[0][1]) + ':' + str(i[1]) + '\n')
    writer.write('\n\nSum: ' + str(np.sum(list(relations.values())))+'\nMean: ' + str(round(np.mean(list(relations.values())),3)) + '\nSD: ' + str(round(np.std(list(relations.values())),3)))
    writer.close()

    Gr.showAll(relaciones, relations, estate_freq(), derivaciones, threshold, time, arrow, frequency, global_freq, info)

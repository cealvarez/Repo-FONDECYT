__author__ = 'Tania'

import pandas as pd
import numpy as np
from datetime import datetime
import operator


class Appointment:
    def __init__(self, patient, time, act, executor, estate, center):
        self.patient = patient
        self.time = time
        self.act = act
        # self.ciap = ciap
        self.executor = executor
        self.estate = estate
        self.center = center
        self.is_trigger = None

    def set_trigger(self, value):
        self.is_trigger = value

patients = {}
#GUARDA TUPLAS ('E',X) QUE INDICAN QUE EL ESTAMENTO 'E' APARECE X VECES EN EL LOG
estate_names = {}
#GUARDA TUPLAS ('A',X) QUE INDICAN QUE LA ACTIVIDAD 'A' SE REALIZO X VECES
act_names = {}
#GUARDA TUPLAS ('R',X) QUE INDICAN QUE EL PROFESIONAL 'R' APARECE X VECES EN EL LOG
res_names = {}
#AGRUPA A LOS PROFESIONALES POR ESTAMENTO
role_dic = {}

role_dic['MEDICO'] = []
role_dic['ENFERMERA'] = []
role_dic['MATRON(A)'] = []
role_dic['NUTRICIONISTA'] = []
role_dic['ODONTOLOGO'] = []
role_dic['KINESIOLOGO'] = []
role_dic['PSICOLOGO/A'] = []
role_dic['TECNICO PARAMEDICO'] = []
role_dic['ASISTENTE SOCIAL'] = []
role_dic['ADMINISTRADOR'] = []
role_dic['ADMINISTRATIVO'] = []
role_dic['SALA DE PROCEDIMIENTOS'] = []

# Log Structure: case | timestamp | activity | executor | estate | center | others...
def readLog(file, start, finish):
    print("LECTURA LOG SIMPLE\n")
    data = pd.read_csv(file, sep=';')
    data['fecha'] = pd.to_datetime(data['fecha'], format="%Y/%m/%d %H:%M")
    data = data.sort_index(by=['id_paciente', 'fecha'])
    data['fecha'] = data['fecha'].apply(lambda x: x.strftime('%Y/%m/%d %H:%M'))

    lista_malos = []
    eventReader = open('Input/Events.txt', 'r')
    for line in eventReader:
        s = line.strip()
        lista_malos.append(s)

    for case, time, act, executor, estate, attended in \
            zip(data['id_paciente'], data['fecha'], data['acto'], data['id_clinico'], data['estamento'], data['vino']):



        if (attended == 0): #SOLO SE CONSIDERA LOS QUE SE ATENDIERON
            continue
        if(estate == 'SALA DE PROCEDIMIENTOS' or estate == 'TECNICO PARAMEDICO'): #NO LOS CONSIDERA RELEVANTES
            continue
        if(act == 'ECG+ESPIROMETRIA'): #SE JUNTARON LAS ACTIVIDADES 'ECG+ESPIROMETRIA' CON 'ECG'
            act = 'ECG'
        if(act == 'I_CURACION_PIE_DIAB'):#SE JUNTARON LAS ACTIVIDADES 'I_CURACION_PIE_DIAB' CON 'I_CURACION_ENFERMERA'
            act = 'I_CURACION_ENFERMERA'

        if(act in lista_malos):
            continue

        year = datetime.strptime(time, "%Y/%m/%d %H:%M").year
        if year < start or year > finish:
            continue
        event = Appointment(case, time, act, executor, estate, 0)

        if case not in patients:
            patients[case] = []
        patients[case].append(event)

        if act not in act_names:
            act_names[act] = 0
        act_names[act] += 1

        if estate not in estate_names:
            estate_names[estate] = 0
        estate_names[estate] += 1

        if executor not in res_names:
            res_names[executor] = 0
        res_names[executor] += 1

        role_dic[estate].append(executor)


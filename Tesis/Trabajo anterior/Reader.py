__author__ = 'Tania'

import pandas as pd
import numpy as np
from datetime import datetime
import operator
import pylab as pl
import math

# This file only reads param files, save data in dictionaries and returns them


class Appointment:
    def __init__(self, patient, time, act, period, executor, estate, center):
        self.patient = patient
        self.time = time
        self.act = act
        self.period = period
        # self.ciap = ciap
        self.executor = executor
        self.estate = estate
        self.center = center
        self.is_trigger = None

    def set_trigger(self, value):
        self.is_trigger = value

# statistics obtained from event log
# Key: cluster. Value: dictionary with the number of occurrences of each estate in the log (estate: freq)
estate_freq = {}

# Key: cluster. Value: dictionary with the number of occurrences of each activity in the log (activity: freq)
act_freq = {}

# Key: cluster. Value: dictionary with the number of occurrences of each professional in the log (professional: freq)
professional_freq = {}

# Key: cluster. Value: dictionary with the list of professionals per estate
estate_professionals = {}

# Key: cluster. Value: dictionary with the number of cv controls per patient
patients_cv = {}

# Key: cluster. Value: explicit derivations
next_appointment = {}

# Key: cluster. Value: dictionary with the list of distinct professional that treat each patient
patient_professionals = {}

# Key: cluster. Value: dictionary with the list of distinct activities per patient
patient_activities = {}

# patient: cluster
patient_cluster = {}

# cluster: patients
cluster_patients = {}

# Key: cluster. Value: dictionary with Key: patient, and Value: a dictionary with the professionals that treat that
# patient and a label that indicates the number of professional
professional_number_in_patient = {}

#Key: patient. Value: dict with key: period and value: total derivations
patient_period_derivations = {}

'''
def restart():
    # patients.clear()
    estate_freq.clear()
    act_freq.clear()
    professional_freq.clear()
    estate_professionals.clear()
    patients_cv.clear()
    next_appointment.clear()
    patient_professionals.clear()
    patient_activities.clear()
'''


def read_clusters(clusters_file, clusters):
    data = pd.read_csv(clusters_file, sep=';')
    for patient, cluster in \
            zip(data['id_paciente'], data['cluster']):
        if str(cluster) not in clusters:
            continue
        patient_cluster[patient] = str(cluster)
        if cluster not in cluster_patients:
            cluster_patients[cluster] = []
        cluster_patients[cluster].append(patient)
    print(len(patient_cluster.keys()))


# Log Structure: case | timestamp | activity | executor | estate | center | others...
def read_log(log_file, start, finish, cv_frequency):
    print("READ LOG\n")

    # Key: cluster. Value: list of patients with their appointments
    log_patients = {}

    # Key: Patient. Value: dictionary with Key: Activity and Value: frequency
    patient_act_frequency = {}

    data = pd.read_csv(log_file, sep=';')
    data['fecha'] = pd.to_datetime(data['fecha'], format="%d-%m-%Y %H:%M")
    #data['fecha'] = pd.to_datetime(data['fecha'], format="%Y/%m/%d %H:%M")
    #data = data.sort_index(by=['id_caso', 'fecha'])
    data = data.sort_index(by=['id_paciente', 'fecha'])
    #data['fecha'] = data['fecha'].apply(lambda x: x.strftime('%Y/%m/%d %H:%M'))
    data['fecha'] = data['fecha'].apply(lambda x: x.strftime('%d/%m/%Y %H:%M'))

    valid_acts = []
    cv_acts = []
    case = ''
    event_reader = open('Input/Events.txt', 'r')
    for line in event_reader:
        s = line.strip()
        valid_acts.append(s)
    act_reader = open('Input/Explicit_Derivation.txt', 'r')
    for line in act_reader:
        s = line.strip()
        cv_acts.append(s)

    profs = []
    corresponding_patient = ""
    corresponding_time = ""

    ###FILA 80525 PACIENTE 14002 20114/06/18 NO TIENE ESTAMENTO
    writer = open('Log/log-detailed.csv', 'w')
    #for period, patient, timestamp, act, executor, estate, relevant, estate_to, next_month in \
    #        zip(data['id_caso'], data['id_paciente'], data['fecha'], data['actividad'], data['medico_id'], data['medico_estamento'],
    #            data['relevante'], data['derivado'], data['mes']):

    for patient, timestamp, act, executor, estate, relevant, estate_to, next_month in \
            zip(data['id_paciente'], data['fecha'], data['actividad'], data['medico_id'], data['medico_estamento'],
                data['relevante'], data['derivado'], data['mes']):


        if relevant == 'NO':
            continue

        if estate == 'LABORATORIO':
            continue

        time = datetime.strptime(timestamp, "%d/%m/%Y %H:%M")
        #time = datetime.strptime(timestamp, "%Y/%m/%d %H:%M")
        appoint_date = time
        #print(appoint_date, patient, estate_to, estate_to != estate_to)
        year = time.year
        month = time.month
        if year < start[1] or year > finish[1]:
            continue
        if (year == start[1] and month < start[0]) or (year == finish[1] and month > finish[0]):
            continue

        if act not in valid_acts:
            continue
        if patient not in patient_cluster:
            continue

        if patient not in patient_period_derivations:
            patient_period_derivations[patient] = {}
        #if period not in patient_period_derivations[patient]:
        #    patient_period_derivations[patient][period] = 0

        cluster = patient_cluster[patient]
        if cluster not in log_patients:
            log_patients[cluster] = {}
            act_freq[cluster] = {}
            estate_freq[cluster] = {}
            professional_freq[cluster] = {}
            estate_professionals[cluster] = {}
            patients_cv[cluster] = {}
            next_appointment[cluster] = {}
            patient_professionals[cluster] = {}
            patient_activities[cluster] = {}
            professional_number_in_patient[cluster] = {}

        patients_list = log_patients[cluster]
        acts_list = act_freq[cluster]
        professionals_list = professional_freq[cluster]
        estates_list = estate_freq[cluster]
        estate_prof_list = estate_professionals[cluster]
        patients_cv_list = patients_cv[cluster]
        patient_professionals_list = patient_professionals[cluster]
        patient_activities_list = patient_activities[cluster]
        professional_number_list = professional_number_in_patient[cluster]
        #event = Appointment(patient, time, act, period, executor, estate, 0)
        event = Appointment(patient, time, act, 1, executor, estate, 0)
        
        #if estate_to != estate_to:
        #    estate_to = 'ANY'
        #if next_month != next_month:
        #    next_month = 0        

        if (act == 'DERIVACION') and estate_to == estate_to and next_month == next_month:

            if cluster not in next_appointment:
                next_appointment[cluster] = {}
            if patient not in next_appointment[cluster]:
                next_appointment[cluster][patient] = []
            if (appoint_date, estate_to, int(next_month)) not in next_appointment[cluster][patient]:
                next_appointment[cluster][patient].append((appoint_date, estate_to, int(next_month)))
                
        if patient not in patients_list:
            patients_list[patient] = []
        patients_list[patient].append(event)

        if act not in acts_list:
            acts_list[act] = 0
        acts_list[act] += 1

        if patient not in patient_act_frequency:
            patient_act_frequency[patient] = {}
        if act not in patient_act_frequency[patient]:
            patient_act_frequency[patient][act] = 0
        patient_act_frequency[patient][act] += 1

        if estate == estate:
            if estate not in estates_list:
                estates_list[estate] = 0
            estates_list[estate] += 1

        if executor not in professionals_list:
            professionals_list[executor] = 0
        professionals_list[executor] += 1

        if act in cv_acts:
            if patient not in patients_cv_list:
                patients_cv_list[patient] = 0
            patients_cv_list[patient] += 1

        if estate not in estate_prof_list:
            estate_prof_list[estate] = []
        estate_prof_list[estate].append(executor)

        if patient not in patient_professionals_list:
            patient_professionals_list[patient] = []
        if executor not in patient_professionals_list[patient]:
            patient_professionals_list[patient].append(executor)

        if patient not in patient_activities_list:
            patient_activities_list[patient] = []
        if act not in patient_activities_list[patient]:
            patient_activities_list[patient].append(act)

        if estate not in profs:
            profs.append(estate)

        if case == '':
            case = str(patient)
            med_count = 1
            enf_count = 1
            nut_count = 1
        elif case != str(patient):
            case = str(patient)
            med_count = 1
            enf_count = 1
            nut_count = 1

        if act == 'CTCV':
            if case not in professional_number_list:
                professional_number_list[case] = {}
            if executor not in professional_number_list[case]:
                if estate == 'MEDICO':
                    professional_number_list[case][executor] = 'MEDICO ' + str(med_count)
                    med_count += 1
                if estate == 'ENFERMERA':
                    professional_number_list[case][executor] = 'ENFERMERA ' + str(enf_count)
                    enf_count += 1
                if estate == 'NUTRICIONISTA':
                    professional_number_list[case][executor] = 'NUTRICIONISTA ' + str(nut_count)
                    nut_count += 1

    sorted_cv_patients = {}
    for cluster in patients_cv:
        sorted_cv_patients[cluster] = sorted(patients_cv[cluster].items(), key=operator.itemgetter(1))

    most_freq_cv = {}
    for cluster in sorted_cv_patients:
        for p in sorted_cv_patients[cluster]:
            if p[1] >= cv_frequency:
                if cluster not in most_freq_cv:
                    most_freq_cv[cluster] = []
                most_freq_cv[cluster].append(str(p[0]))

    for prof in professional_number_in_patient:
        for case in professional_number_in_patient[prof]:
            writer.write(str(prof) + ';' + str(case) + ';')
            for k in professional_number_in_patient[prof][case]:
                writer.write(k.replace('"', '') + ' ' + str(professional_number_in_patient[prof][case][k]) + ';')
            writer.write('jijixd\n')
    writer.close()

    writer = open('Reports/Explicit Derivation/referrals.txt', 'w')

    for cluster in next_appointment:
        appointments = sorted(next_appointment[cluster].items(), key=operator.itemgetter(0))
        s = 'Cluster: ' + cluster
        writer.write(s + '\n')
        writer.write('date;referral_to;month\n')
        for a in appointments:
            s = str(a[0]) + '\n'
            for j in a[1]:
                s += str(j[0])+';'+str(j[1])+';'+str(int(j[2]))+'\n'
            writer.write(s + '\n')
    writer.close()

    '''
    for cluster in cluster_patients:
        writer2 = open('Reports/Implicit Derivation/activity_report ' + str(cluster) +'.csv', 'w')
        writer2.write('PATIENT;')
        for i in range(len(valid_acts)):
            writer2.write(valid_acts[i])
            if i < len(valid_acts) - 1:
                writer2.write(';')
        writer2.write('\n')
        for iter_patient in cluster_patients[cluster]:
            if iter_patient not in patient_act_frequency:
                continue
            writer2.write(str(iter_patient)+';')
            for i in range (len(valid_acts)):
                act = valid_acts[i]
                if act in patient_act_frequency[iter_patient]:
                    writer2.write(str(patient_act_frequency[iter_patient][act]))
                else:
                    writer2.write('0')
                if i < len(valid_acts) - 1:
                    writer2.write(';')
            writer2.write('\n')

        writer2.close()
    '''


    return log_patients, most_freq_cv, next_appointment


def read_referrals(referrals_file, start, finish):
    data = pd.read_csv(referrals_file, sep=';')
    data['fecha'] = pd.to_datetime(data['fecha'], format="%Y/%m/%d")
    data = data.sort_index(by=['id_paciente', 'fecha'])
    data['fecha'] = data['fecha'].apply(lambda x: x.strftime('%Y/%m/%d'))

    for patient, time, executor, estate, next_month in \
            zip(data['id_paciente'], data['fecha'], data['derivador'],
                data['derivado'], data['mes']):

        appoint_date = datetime.strptime(time, "%Y/%m/%d")
        year = appoint_date.year
        month = appoint_date.month
        if year < start[1] or year > finish[1]:
            continue
        if (year == start[1] and month < start[0]) or (year == finish[1] and month > finish[0]):
            continue

        if patient not in patient_cluster:
            continue

        cluster = patient_cluster[patient]

        if cluster not in next_appointment:
            next_appointment[cluster] = {}
        if patient not in next_appointment[cluster]:
            next_appointment[cluster][patient] = []
        if (time, estate, int(next_month)) not in next_appointment[cluster][patient]:
            next_appointment[cluster][patient].append((appoint_date, estate, int(next_month)))

    writer = open('Reports/Explicit Derivation/referrals.txt', 'w')

    for cluster in next_appointment:
        appointments = sorted(next_appointment[cluster].items(), key=operator.itemgetter(0))
        s = 'Cluster: ' + cluster
        writer.write(s + '\n')
        for a in appointments:
            s = str(a[0]) + '\n'
            for j in a[1]:
                s += '('+str(j[0])+')->('+str(j[1])+','+str(int(j[2]))+')\n'
            writer.write(s + '\n')
    writer.close()

    return next_appointment


def read_dm_compensation_t90(dm_file, center_param, min_age, max_age, start, finish, min_number_of_total_tests):
    patients_age = {}
    patients_gender = {}
    dm_patients = {}

    data = pd.read_csv(dm_file, sep=';')
    data['fecha'] = pd.to_datetime(data['fecha'], format="%Y/%m/%d")
    data = data.sort_index(by=['id_paciente', 'fecha'])
    data['fecha'] = data['fecha'].apply(lambda x: x.strftime('%Y/%m/%d'))

    prev_id = 0

    for center, sector, patient, date, hba1c, condition, age, gender in \
            zip(data['centro'], data['sector'], data['id_paciente'], data['fecha'], data['examen_hba1c'],
                data['dm_compensacion'], data['edad_paciente'], data['sexo']):
        if center != center_param and center_param != 'X':
            continue

        if age < min_age or age > max_age:
            continue

        date = datetime.strptime(date, "%Y/%m/%d")
        year = date.year
        month = date.month
        if year < start[1] or year > finish[1]:
            continue
        if (year == start[1] and month < start[0]) or (year == finish[1] and month > finish[0]):
            continue
        if patient not in patient_cluster:
            continue
        cluster = patient_cluster[patient]
        if cluster not in dm_patients:
            dm_patients[cluster] = {}

        if patient != prev_id:
            prev_id = patient
            dm_patients[cluster][patient] = []
            patients_age[patient] = age
            patients_gender[patient] = gender
        dm_patients[cluster][patient].append([date, round(float(hba1c), 1), condition])

    # remove patients with very few measurements and save the first and last date for the other patients
    for cluster in dm_patients:
        remove_keys = []
        for patient in dm_patients[cluster]:
            if len(dm_patients[cluster][patient]) < min_number_of_total_tests:
                remove_keys.append(patient)
        for key in remove_keys:
            del dm_patients[cluster][key]
            del patients_age[key]
            del patients_gender[key]

    return dm_patients

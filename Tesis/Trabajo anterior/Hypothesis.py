__author__ = 'Tania'

import Reader
import DMCompensation_filter
from datetime import datetime
import operator
import csv
import numpy as np


# Input
official_list = []
patients_log = {}
patients_dm = {}
patients_dm_periods = {}
patients_age = {}
patients_gender = {}

# Metrics


# used and/or complete by function number_of_professionals():
keys_aux = {'doctor': 0, 'nurse': 1, 'nutritionist': 2}


professionals_duration = {'doctor': {}, 'nurse': {}, 'nutritionist': {}}


# Start: Read data
def read_data():
    global patients_log
    Reader.readLog(file='Input/Log-completo.csv', start=2014, finish=2015, cv_frequency=0)
    patients_log = Reader.patients

    global patients_dm, patients_dm_periods, patients_age, patients_gender
    patients_dm, patients_dm_periods, patients_age, patients_gender = DMCompensation_filter.set_data()

    patients_official_list()


# list of patients with hba1c register and log register
def patients_official_list():
    global official_list
    for patient in patients_dm:
        if patient in patients_log:
            official_list.append(patient)


# DM CUBE: PATIENTS' HbA1C VALUES
# Average hba1c and number of hba1c tests:
def average_hba1c():
    avg_hba1c = {}
    hba1c_number = {}
    for patient in patients_dm:
        avg_hba1c[patient] = round(np.average([row[1] for row in patients_dm[patient]]), 1)
        hba1c_number[patient] = len(patients_dm[patient])

    return avg_hba1c, hba1c_number


# First & Last hba1c:
def first_last_hba1c():
    lt_hba1c = {}
    ft_hba1c = {}
    for patient in patients_dm:
        ft_hba1c[patient] = patients_dm[patient][0][1]
        lt_hba1c[patient] = patients_dm[patient][len(patients_dm[patient])-1][1]

    return ft_hba1c, lt_hba1c


# % compensated tests:
def compensated_test_percentage():
    tests_percentage = {}
    for patient in patients_dm:
        count = 0
        for test in patients_dm[patient]:
            if test[2] == 1:
                count += 1

        tests_percentage[patient] = round(100*count/len(patients_dm[patient]), 1)

    return tests_percentage


# total number of months per patient:
def total_30d_months():
    tot_months = {}
    for patient in patients_dm_periods:
        tot_months[patient] = len(patients_dm_periods[patient])

    return tot_months


# % compensated months
def compensated_months_percentage():
    months_percentage = {}
    for patient in patients_dm_periods:
        count = 0
        for period in range(len(patients_dm_periods[patient])):
            if patients_dm_periods[patient][period] is not None and \
                    (patients_dm_periods[patient][period][1] == 1 or patients_dm_periods[patient][period][1] == 'C'):
                count += 1

        months_percentage[patient] = round(100*count/len(patients_dm_periods[patient]), 1)

    return months_percentage


# % times that patient did get worst
def times_worst_percentage(delta):
    times_percentage = {}
    for patient in patients_dm:
        count = 0
        if len(patients_dm[patient]) < 2:
            times_percentage[patient] = '-'
            continue
        for index in range(len(patients_dm[patient])-1):
            test1 = patients_dm[patient][index][1]
            test2 = patients_dm[patient][index+1][1]
            if test2 - test1 >= delta:
                count += 1
        times_percentage[patient] = round(100*count/(len(patients_dm[patient])-1), 1)

    return times_percentage


# average number of consecutive months during which the patient is compensated
def average_months_compensated():
    avg_months_c = {}
    avg_months_d = {}
    for patient in patients_dm_periods:
        print('PATIENT ', patient)
        count_c = 0
        count_d = 0
        avg_months_c[patient] = []
        avg_months_d[patient] = []
        for period in range(len(patients_dm_periods[patient])):
            if patients_dm_periods[patient][period] is not None and \
                    (patients_dm_periods[patient][period][1] == 1 or patients_dm_periods[patient][period][1] == 'C'):
                count_c += 1
                if count_d > 0:
                    avg_months_d[patient].append(count_d)
                    print('D ', count_d)
                    count_d = 0

            elif patients_dm_periods[patient][period] is not None and \
                    (patients_dm_periods[patient][period][1] == 0 or patients_dm_periods[patient][period][1] == 'D'):
                count_d += 1
                if count_c > 0:
                    avg_months_c[patient].append(count_c)
                    print('C ', count_c)
                    count_c = 0
            else:  # if is None
                if count_c > 0:
                    avg_months_c[patient].append(count_c)
                    print('C ', count_c)
                    count_c = 0

        if count_c > 0:
            avg_months_c[patient].append(count_c)
            print('C ', count_c)
            count_c = 0
        else:  # count_d > 0
            avg_months_d[patient].append(count_d)
            print('D ', count_d)
            count_d = 0

    for patient in avg_months_c:
        if len(avg_months_c[patient]) > 0:
            avg = np.average(avg_months_c[patient])
        else:
            avg = 0
        avg_months_c[patient] = avg

        if len(avg_months_d[patient]) > 0:
            avg = np.average(avg_months_d[patient])
        else:
            avg = 0
        avg_months_d[patient] = avg

    return avg_months_c, avg_months_d


# Histogram frequencies CORREGIR PQ NO ESTA TOMANDO LA ULTIMA PASADA
def dd_and_cc_consecutive_months_freq():
    cc_months = {}
    dd_months = {}
    dd_list = []
    cc_list = []
    for patient in patients_dm_periods:
        count_c = 0
        count_d = 0

        for period in range(len(patients_dm_periods[patient])):
            if patients_dm_periods[patient][period] is not None and \
                    (patients_dm_periods[patient][period][1] == 1 or patients_dm_periods[patient][period][1] == 'C'):
                count_c += 1
                if count_d > 0:
                    if count_d not in dd_months:
                        dd_months[count_d] = 0
                    dd_months[count_d] += 1
                    dd_list.append(count_d)
                    count_d = 0
            elif patients_dm_periods[patient][period] is not None and \
                    (patients_dm_periods[patient][period][1] == 0 or patients_dm_periods[patient][period][1] == 'D'):
                count_d += 1
                if count_c > 0:
                    if count_c not in cc_months:
                        cc_months[count_c] = 0
                    cc_months[count_c] += 1
                    cc_list.append(count_c)
                    count_c = 0

    return dd_months, cc_months  # dd_list, cc_list


# LOG: PATIENTS' ATTENTIONS
# Returns the number of days between two dates
def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y/%m/%d %H:%M")
    d2 = datetime.strptime(d2, "%Y/%m/%d %H:%M")

    return abs((d2 - d1).days)


# Aux function REVISAR ANTES DE USAR
def set_professional_duration():
    for estate in list(professionals_duration.keys()):
        for professional in list(professionals_duration[estate].keys()):
            d1 = professionals_duration[estate][professional][0]
            d2 = professionals_duration[estate][professional][1]
            professionals_duration[estate][professional] = days_between(d1, d2)


# number of attentions per estate and duration of each professional
def attentions_per_estate():
    # for each estate (doctor, nurse and nutritionist), for each patient: the number of attentions
    patients_estate = {}
    patients_total_cv_attentions = {}  # Total amount of medical care, carried out by cardiovascular professional team
    patients_total_attentions = {}  # Total amount of medical care, carried out by any professional
    patients_total_dupla_attentions = {}
    patients_total_visiting_attentions = {}
    patients_total_family_attentions = {}
    patients_total_familyInCharge_attentions = {}

    for patient in patients_log:
        # To avoid considering duplicate attentions
        added_tuples = set()
        patients_estate[patient] = [0, 0, 0]
        patients_total_attentions[patient] = 0
        patients_total_cv_attentions[patient] = 0
        patients_total_dupla_attentions[patient] = 0
        patients_total_visiting_attentions[patient] = 0
        patients_total_family_attentions[patient] = 0
        patients_total_familyInCharge_attentions[patient] = 0
        for event in patients_log[patient]:
            if (event.executor, event.time) in added_tuples:
                continue
            else:
                added_tuples = added_tuples.union({(event.executor, event.time)})

            patients_total_attentions[patient] += 1

            if event.act == 'DUPLA' and (patient, event.act, event.time) not in added_tuples:
                patients_total_dupla_attentions[patient] += 1
                added_tuples = added_tuples.union({(patient, event.act, event.time)})
            elif event.act == 'VISITA DOMICILIARIA':
                patients_total_visiting_attentions[patient] += 1
            elif event.act == 'ATENCION FAMILIAR':
                patients_total_family_attentions[patient] += 1
            elif event.act == 'ENCARGADO DE FAMILIA':
                patients_total_familyInCharge_attentions[patient] += 1

            if event.estate == 'MEDICO':
                estate_aux = 'doctor'
            elif event.estate == 'ENFERMERA':
                estate_aux = 'nurse'
            elif event.estate == 'NUTRICIONISTA':
                estate_aux = 'nutritionist'
            else:
                continue

            patients_total_cv_attentions[patient] += 1
            patients_estate[patient][keys_aux[estate_aux]] += 1

            # calculate time horizon of each professional
            if event.executor not in professionals_duration[estate_aux]:
                professionals_duration[estate_aux][event.executor] = [event.time, event.time]
            else:
                professionals_duration[estate_aux][event.executor] = \
                    [min(professionals_duration[estate_aux][event.executor][0], event.time),
                     max(professionals_duration[estate_aux][event.executor][1], event.time)]

    set_professional_duration()

    return patients_estate, patients_total_attentions, patients_total_cv_attentions, patients_total_dupla_attentions, patients_total_visiting_attentions, patients_total_family_attentions, patients_total_familyInCharge_attentions


# number of distinct professionals per state
def number_of_professionals():
    patients_doctors = {}
    patients_nurses = {}
    patients_nutritionists = {}
    patients_doctors_number = {}
    patients_nurses_number = {}
    patients_nuts_number = {}
    patient_estate_changes = {}  # Key: patient, Value: [doctor, nurse, nutritionist] changes
    patient_estate_sequence = {}

    previous_estate = {}

    for patient in patients_log:
        patients_doctors[patient] = {}
        patients_nurses[patient] = {}
        patients_nutritionists[patient] = {}
        patients_doctors_number[patient] = 0
        patients_nurses_number[patient] = 0
        patients_nuts_number[patient] = 0
        patient_estate_changes[patient] = [0, 0, 0]
        patient_estate_sequence[patient] = ['', '', '']
        previous_estate['doctor'] = 0
        previous_estate['nurse'] = 0
        previous_estate['nutritionist'] = 0
        # To avoid considering duplicate attentions
        added_tuples = set()
        for event in patients_log[patient]:
            if event.estate == 'MEDICO':
                patients_aux = patients_doctors
                patients_number = patients_doctors_number
                estate_aux = 'doctor'
            elif event.estate == 'ENFERMERA':
                patients_aux = patients_nurses
                patients_number = patients_nurses_number
                estate_aux = 'nurse'
            elif event.estate == 'NUTRICIONISTA':
                patients_aux = patients_nutritionists
                patients_number = patients_nuts_number
                estate_aux = 'nutritionist'
            else:
                continue

            if (event.executor, event.time) in added_tuples:
                continue
            else:
                added_tuples = added_tuples.union({(event.executor, event.time)})

            if event.executor not in patients_aux[patient]:
                patients_aux[patient][event.executor] = [0, 0, 0]  # [number of attentions, start, end]
                patients_number[patient] += 1
            patients_aux[patient][event.executor][0] += 1
            # setting start [1] and end [2] dates:
            if patients_aux[patient][event.executor][1] == 0:
                patients_aux[patient][event.executor][1] = event.time
            patients_aux[patient][event.executor][2] = event.time

            if previous_estate[estate_aux] != 0 and previous_estate[estate_aux] != event.executor:
                patient_estate_changes[patient][keys_aux[estate_aux]] += 1
            previous_estate[estate_aux] = event.executor

            patient_estate_sequence[patient][keys_aux[estate_aux]] += str(event.executor) + '-'

    return patient_estate_changes, patient_estate_sequence, patients_doctors_number, patients_nurses_number, \
           patients_nuts_number


# average days between attentions #REVISADO: OK
def time_between_attentions():
    estate_attentions = {}
    attentions_cv = {}
    max_delta = 0

    for patient in patients_log:
        added_tuples = set()
        attentions_cv[patient] = []
        estate_attentions[patient] = [[], [], []]
        for index in range(len(patients_log[patient])):
            added = False
            event1 = patients_log[patient][index]
            if event1.estate == 'MEDICO':
                estate_aux = 'doctor'
            elif event1.estate == 'ENFERMERA':
                estate_aux = 'nurse'
            elif event1.estate == 'NUTRICIONISTA':
                estate_aux = 'nutritionist'
            else:
                continue

            if (event1.executor, event1.time) in added_tuples:
                continue
            else:
                added_tuples = added_tuples.union({(event1.executor, event1.time)})

            # look for the next cardiovascular care
            for i in range(index+1, len(patients_log[patient])):
                event2 = patients_log[patient][i]
                if not(event2.estate == 'MEDICO') and not(event2.estate == 'ENFERMERA') and not(event2.estate == 'NUTRICIONISTA'):
                    continue
                if (event2.executor, event2.time) in added_tuples:
                    continue

                if not added:
                    days = days_between(event1.time, event2.time)
                    max_delta = max(max_delta, days)
                    attentions_cv[patient].append(days)
                    added = True

                if event1.estate == event2.estate:
                    days = days_between(event1.time, event2.time)
                    max_delta = max(max_delta, days)
                    estate_attentions[patient][keys_aux[estate_aux]].append(days)
                    break

    for patient in attentions_cv:
        if len(attentions_cv[patient]) > 0:
            avg = round(np.average(attentions_cv[patient]), 1)
        else:
            avg = max_delta*2
        attentions_cv[patient] = avg
        for estate in keys_aux:
            if len(estate_attentions[patient][keys_aux[estate]]) > 0:
                avg = round(np.average(estate_attentions[patient][keys_aux[estate]]),1)
            else:
                avg = max_delta*2
            estate_attentions[patient][keys_aux[estate]] = avg

    return estate_attentions, attentions_cv

# average days between attentions #REVISADO: OK
def time_between_special_attentions():
    dupla_attentions = {}
    visiting_attentions = {}
    family_attentions = {}
    familyInCharge_attentions = {}
    max_delta_dupla = 0
    max_delta_visiting = 0
    max_delta_family = 0
    max_delta_familyInCharge = 0

    for patient in patients_log:
        added_tuples = set()
        dupla_attentions[patient] = []
        visiting_attentions[patient] = []
        family_attentions[patient] = []
        familyInCharge_attentions[patient] = []
        for index in range(len(patients_log[patient])):
            added = False
            event1 = patients_log[patient][index]
            if event1.act not in ['DUPLA', 'VISITA DOMICILIARIA', 'ENCARGADO DE FAMILIA', 'ATENCION FAMILIAR']:
                continue
            if (patient, event1.executor, event1.time) in added_tuples:
                continue
            else:
                added_tuples = added_tuples.union({(patient, event1.executor, event1.time)})
            # look for the next cardiovascular care
            for i in range(index+1, len(patients_log[patient])):
                event2 = patients_log[patient][i]
                if (patient, event2.executor, event2.time) in added_tuples:
                    continue

                if not added and event2.act == event1.act:
                    days = days_between(event1.time, event2.time)
                    if event1.act == 'DUPLA':
                        dupla_attentions[patient].append(days)
                        max_delta_dupla = max(max_delta_dupla, days)
                    elif event1.act == 'VISITA DOMICILIARIA':
                        visiting_attentions[patient].append(days)
                        max_delta_visiting = max(max_delta_visiting, days)
                    elif event1.act == 'ATENCION FAMILIAR':
                        family_attentions[patient].append(days)
                        max_delta_family = max(max_delta_family, days)
                    elif event1.act == 'ENCARGADO DE FAMILIA':
                        familyInCharge_attentions[patient].append(days)
                        max_delta_familyInCharge = max(max_delta_familyInCharge, days)
                    added = True

    for patient in dupla_attentions:
        if len(dupla_attentions[patient]) > 0:
            avg = round(np.average(dupla_attentions[patient]), 1)
        else:
            avg = 2*max_delta_dupla
        dupla_attentions[patient] = avg

    for patient in visiting_attentions:
        if len(visiting_attentions[patient]) > 0:
            avg = round(np.average(visiting_attentions[patient]), 1)
        else:
            avg = 2*max_delta_visiting
        visiting_attentions[patient] = avg

    for patient in familyInCharge_attentions:
        if len(familyInCharge_attentions[patient]) > 0:
            avg = round(np.average(familyInCharge_attentions[patient]), 1)
        else:
            avg = 2*max_delta_familyInCharge
        familyInCharge_attentions[patient] = avg

    for patient in family_attentions:
        if len(family_attentions[patient]) > 0:
            avg = round(np.average(family_attentions[patient]), 1)
        else:
            avg = 2*max_delta_family
        family_attentions[patient] = avg

    return dupla_attentions, visiting_attentions, family_attentions, familyInCharge_attentions


def calculate_attentions_metrics(reference, attentions):
    metrics = {}

    for patient in patients_log:
        if attentions[patient] != 0:
            metrics[patient] = round((attentions[patient]-(reference[patient]-1))/attentions[patient], 2)
        else:
            metrics[patient] = 0

    return metrics


def calculate_changes_metrics(reference, attentions):
    metrics = {}

    for patient in patients_log:
        if attentions[patient] != 0:
            metrics[patient] = round((attentions[patient]-(reference[patient]))/attentions[patient], 2)
        else:
            metrics[patient] = 0

    return metrics


# REPORTS: sorting criteria is a dictionary: {patient: metrics}; columns is a list of dictionaries {patient: value}
def write_report(header, columns, sorting_criteria, name, separator):

    # patients are ordered by their number of total attentions
    sorted_patients = sorted(sorting_criteria, key=sorting_criteria.get, reverse=True)

    report = open('Log/new/' + name + '.csv', 'w')
    wr = csv.writer(report, delimiter=separator)
    wr.writerow(header)
    for patient in sorted_patients:
        if patient not in official_list:
            continue
        line = [patient, patients_age[patient], patients_gender[patient]]
        for col in columns:
            value = col[patient]
            line.append(value)
        wr.writerow(line)
    report.close()


def get_cols_from_dic(dic):
    doctor = {}
    nurse = {}
    nutritionist = {}
    for patient in patients_log:
        doctor[patient] = dic[patient][0]
        nurse[patient] = dic[patient][1]
        nutritionist[patient] = dic[patient][2]

    return doctor, nurse, nutritionist


# New code
def generate_report():
    read_data()
    header = ['id_paciente', 'edad', 'sexo','atenciones_total', 'atenciones_cardio', 'atenciones_dupla', 'atenciones_vis_dom', 'atenciones_familiar', 'atenciones_enc_fam', 'atenciones_medico', 'atenciones_enfermera',
              'atenciones_nutricionista', 'numero_medicos', 'numero_enfermeras', 'numero_nutricionistas', 'cambios_medico',
              'cambios_enfermera', 'cambios_nutricionista', 'metrica_numero_medicos', 'metrica_numero_enfermeras',
              'metrica_cambios_medico', 'metrica_cambios_enfermera', 'nro meses', 'nro. mediciones hba1c', 'hba1c_promedio', 'primer hba1c','ultimo hba1c' , 'p_mediciones_C', 'p_meses_tot_C',
              'delta_atenciones_total', 'delta_atenciones_medico', 'delta_atenciones_enfermera',
              'delta_atenciones_nutricionista', 'delta_atenciones_dupla', 'delta_atenciones_visita', 'delta_atenciones_familiares', 'delta_atenciones_enc_familia', 'p_veces_peor', 'promedio_meses_seguidos_C', 'promedio_meses_seguidos_D']

    estate, total_attentions, total_cv_attentions, total_dupla_attentions, total_visiting_attentions, total_family_attentions, total_familyInCharge_attentions = attentions_per_estate()
    doc_a, nur_a, nut_a = get_cols_from_dic(estate)
    columns = [total_attentions, total_cv_attentions, total_dupla_attentions, total_visiting_attentions, total_family_attentions, total_familyInCharge_attentions, doc_a, nur_a, nut_a]

    changes, sequence, doctors_number, nurses_number, nuts_number = number_of_professionals()
    doc, nur, nut = get_cols_from_dic(changes)
    columns.append(doctors_number)
    columns.append(nurses_number)
    columns.append(nuts_number)
    columns.append(doc)
    columns.append(nur)
    columns.append(nut)

    number_metrics = calculate_attentions_metrics(doctors_number, doc_a)
    columns.append(number_metrics)
    number_metrics = calculate_attentions_metrics(nurses_number, nur_a)
    columns.append(number_metrics)

    changes_metrics = calculate_changes_metrics(doc, doc_a)
    columns.append(changes_metrics)
    changes_metrics = calculate_changes_metrics(nur, nur_a)
    columns.append(changes_metrics)

    months_number = total_30d_months()
    hba1c_avg, hba1c_number = average_hba1c()
    first_hba1c, last_hba1c = first_last_hba1c()
    tests = compensated_test_percentage()
    months = compensated_months_percentage()

    columns.append(months_number)
    columns.append(hba1c_number)
    columns.append(hba1c_avg)
    columns.append(first_hba1c)
    columns.append(last_hba1c)
    columns.append(tests)
    columns.append(months)

    estate_delta, cv_delta = time_between_attentions()
    doc, nur, nut = get_cols_from_dic(estate_delta)
    columns.append(cv_delta)
    columns.append(doc)
    columns.append(nur)
    columns.append(nut)

    dupla_delta, visiting_delta, family_delta, familyInCharge_delta = time_between_special_attentions()
    columns.append(dupla_delta)
    columns.append(visiting_delta)
    columns.append(family_delta)
    columns.append(familyInCharge_delta)

    percentage = times_worst_percentage(0.5)
    columns.append(percentage)

    avg_c, avg_d = average_months_compensated()
    columns.append(avg_c)
    columns.append(avg_d)

    write_report(header, columns, total_cv_attentions, 'complete_report', ';')

generate_report()


# DISCO
def write_disco_file():
    report = open('Log/new/disco_status.csv', 'w', newline='')
    wr = csv.writer(report, delimiter=';')
    line = ['patient_id', 'status']
    wr.writerow(line)
    for patient in patients_dm_periods:
        for period in range(len(patients_dm_periods[patient])):
            if patients_dm_periods[patient][period] is not None:
                line = [patient, patients_dm_periods[patient][period][1]]
            else:
                line = [patient, 'X']
            wr.writerow(line)
    report.close()

#read_data()
#write_disco_file()


# HISTOGRAMS
def write_hist_file(dic, name):
    report = open('Log/new/histograma_' + name + '.csv', 'w', newline='')
    wr = csv.writer(report, delimiter=';')
    line = ['n_meses', 'frec']
    wr.writerow(line)
    for month in dic:
        line = [str(month)+' meses'+name, dic[month]]
        wr.writerow(line)
    report.close()

#read_data()
#dd, cc = dd_and_cc_consecutive_months()
#write_hist_file(dd, 'dd')
#write_hist_file(cc, 'cc')


def log_with_last_hba1c():
    log = open('Log/new/Log_hba1c' + '.csv', 'w', newline='')
    wr = csv.writer(log, delimiter=';')
    line = ['id_paciente', 'fecha', 'actividad', 'ejecutor', 'estamento', 'centro', 'ultima_hba1c']
    wr.writerow(line)
    read_data()
    for patient in patients_log:
        if patient in patients_dm:
            for attention in patients_log[patient]:
                hba1c = '-'
                date_log = datetime.date(datetime.strptime(attention.time, "%Y/%m/%d %H:%M"))
                for test in patients_dm[patient]:
                    date_dm = datetime.date(test[0])
                    if date_dm > date_log:
                        break
                    else:
                        hba1c = test[1]
                line = [patient, attention.time, attention.act, attention.executor, attention.estate, attention.center,
                        hba1c]
                wr.writerow(line)
    log.close()

#log_with_last_hba1c()












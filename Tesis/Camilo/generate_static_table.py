__author__ = 'Tania'

import pandas as pd
import csv
from datetime import datetime
import numpy as np

# Output: id_paciente | sexo | nacimiento | edad | centro | sector | fecha_t90 | edad_t90 | anos_con_t90 | ..
# ..indice de severidad | indice de comorbilidad

# Input files to generate static table:
# 1. Diagnosis: id_paciente | fecha | ciap
diagnosis_file = 'Files/diagnostico_3369.csv'
# 2. Patients: id_paciente | sexo | nacimiento | centro | sector
patients_file = 'Files/paciente_3369.csv'
# 3. DM Patients (studied patients): id_paciente
patients_dm_file = 'Files/paciente_dm_3369.csv'

# Reference date to calculate the indices
diagnosis_max_date = pd.to_datetime('07-11-2016', format="%d-%m-%Y").date()

# Parameters: categories for comorbidities and other diseases (DMT2's severities)
severity_cat = ['cardiovascular', 'nefropatia', 'retinopatia', 'enf_periferica', 'acv', 'neuropatia', 'desorden_metab']
comorbidity_cat = ['cancer', 'enf_pulmonar', 'gastrointestinal', 'musculo_esqueletica', 'enf_mental', 'abuso_sustancia']

severity_ciaps = {'cardiovascular': [['K74', 1], ['K75', 2], ['K76', 1], ['K77', 2], ['K78', 2], ['K79', 2], ['K80', 2],
                                     ['K84', 2], ['K91', 1], ['K92', 1], ['K99', 2]],
                  'nefropatia': [['U06', 1], ['U88', 1], ['U99', 2]],
                  'retinopatia': [['F82', 2], ['F83', 1], ['F84', 1]],
                  'enf_periferica': [['S97', 2]],
                  'acv': [['K89', 1], ['K90', 2]],
                  'neuropatia': [['N93', 1], ['N94', 1]],
                  'desorden_metab': [['T87', 2]]}

comorbidity_ciaps = {'cancer': ['A79', 'B72', 'D74', 'F74', 'H75', 'L71', 'K72', 'N74', 'R84', 'R85', 'S77', 'T71',
                                'T93', 'U75', 'U76', 'U77', 'U79', 'W72', 'X75', 'X76', 'X77', 'X81', 'Y77', 'Y78'],
                     'enf_pulmonar': ['R95', 'R96'],
                     'gastrointestinal': ['D84', 'D86', 'D99'],
                     'musculo_esqueletica': ['L84', 'L88', 'L89', 'L90', 'L91', 'L99'],
                     'enf_mental': ['P01', 'P02', 'P27', 'P70', 'P71', 'P72', 'P73', 'P74', 'P76', 'P77'],
                     'abuso_sustancia': ['P15', 'P16', 'P19', 'Z13']}

# Includes all previous codes (valid ciaps) in two lists
valid_ciaps = ['T90']
for cat in severity_ciaps:
    for code in severity_ciaps[cat]:
        ciap = code[0]
        if ciap not in valid_ciaps:
            valid_ciaps.append(ciap)

for cat in comorbidity_ciaps:
    for ciap in comorbidity_ciaps[cat]:
        if ciap not in valid_ciaps:
            valid_ciaps.append(ciap)

patients_log = {}
diagnosis = {}  # {code: [[patient, date], ...]}
cat_severity_before = {}
cat_severity_after = {}
cat_severity_total = {}
cat_comorbidity_before = {}
cat_comorbidity_after = {}
cat_comorbidity_total = {}

severity_index_category = {}
severity_index = {}
comorbidity_index_category = {}
comorbidity_index = {}


# Gets the ids of studied patients
def read_patient_dm():
    reader = open(patients_dm_file, 'r')
    for line in reader:
        if line.strip() == "id_paciente":
            continue
        patient = int(line.strip())
        if patient not in patients_log:
            patients_log[patient] = []

            cat_severity_before[patient] = {}
            cat_severity_after[patient] = {}
            cat_severity_total[patient] = {}
            cat_comorbidity_before[patient] = {}
            cat_comorbidity_after[patient] = {}
            cat_comorbidity_total[patient] = {}
            severity_index_category[patient] = {}
            severity_index[patient] = {}
            comorbidity_index_category[patient] = {}
            comorbidity_index[patient] = {}

            for cat in severity_cat:
                cat_severity_before[patient][cat] = 0
                cat_severity_after[patient][cat] = 0
                cat_severity_total[patient][cat] = 0
                severity_index_category[patient][cat] = 0
                severity_index[patient][cat] = 0

            for cat in comorbidity_cat:
                cat_comorbidity_before[patient][cat] = 0
                cat_comorbidity_after[patient][cat] = 0
                cat_comorbidity_total[patient][cat] = 0
                comorbidity_index_category[patient][cat] = 0
                comorbidity_index[patient][cat] = 0

    reader.close()
    print("Number of studied/selected patients: ", len(patients_log))


# Read the file that contains the complete data about each patient
def read_patient():
    count = 0
    data = pd.read_csv(patients_file, sep=';')
    data['nacimiento'] = pd.to_datetime(data['nacimiento'], format="%d-%m-%Y")
    for patient, sex, birth, center, team in \
                zip(data['id_paciente'], data['sexo'], data['nacimiento'], data['centro'], data['sector']):
        if patient not in patients_log:
            continue
        birth = birth.date()
        age = 2016 - birth.year
        patients_log[patient] += [sex, birth, age, center, team]
        count += 1
    print("Number of selected patients in patients table", count)


# Reads diagnosis (for valid ciaps) of selected patients until the max date parameter
def read_diagnosis():
    data = pd.read_csv(diagnosis_file, sep=';')
    data['fecha'] = pd.to_datetime(data['fecha'], format="%d-%m-%Y")
    data = data.sort_index(by=['id_paciente', 'fecha'])
    for patient, date, code in \
                zip(data['id_paciente'], data['fecha'], data['ciap']):
        date = date.date()
        if date > diagnosis_max_date:
            continue
        if patient not in patients_log:
            continue
        if code not in valid_ciaps:
            continue
        if code != 'T90':
            if code not in diagnosis:
                diagnosis[code] = []
            # Comorbidities are diagnosed only once
            if patient not in [row[0] for row in diagnosis[code]]:
                diagnosis[code].append([patient, date])
        else:
            if len(patients_log[patient]) < 8:
                # If there are 2 or more dates for T90 diagnosis, it uses the first one
                t90_date = date
                t90_years = 2016-t90_date.year
                t90_age = date.year - patients_log[patient][1].year
                patients_log[patient] += [t90_date, t90_age, t90_years]


def read_files():
    read_patient_dm()
    read_patient()
    read_diagnosis()


# Calculates severity index and comorbidity index
def static_patients():
    for category in severity_ciaps:
        for code in severity_ciaps[category]:
            ciap = code[0]
            score = code[1]
            if ciap not in diagnosis:
                continue
            patients_list = diagnosis[ciap]
            for patient_tuple in patients_list:
                patient_id = patient_tuple[0]
                severity_index_category[patient_id][category] += score
                if severity_index[patient_id][category] < 2:
                    severity_index[patient_id][category] = score

                if len(patients_log[patient_id]) < 6:
                    continue
                date = patient_tuple[1]
                t90_date = patients_log[patient_id][5]
                if date >= t90_date:
                    cat_severity_after[patient_id][category] += 1
                else:
                    cat_severity_before[patient_id][category] += 1
                cat_severity_total[patient_id][category] += 1

    for patient in severity_index:
        severity_index[patient] = sum(severity_index[patient].values())

    for category in comorbidity_ciaps:
        for ciap in comorbidity_ciaps[category]:
            if ciap not in diagnosis:
                continue
            patients_list = diagnosis[ciap]
            for patient_tuple in patients_list:
                patient_id = patient_tuple[0]
                comorbidity_index_category[patient_id][category] += 1
                if comorbidity_index[patient_id][category] < 1:
                    comorbidity_index[patient_id][category] = 1

                if len(patients_log[patient_id]) < 6:
                    continue
                date = patient_tuple[1]
                t90_date = patients_log[patient_id][5]
                if date >= t90_date:
                    cat_comorbidity_after[patient_id][category] += 1
                else:
                    cat_comorbidity_before[patient_id][category] += 1
                cat_comorbidity_total[patient_id][category] += 1

    for patient in comorbidity_index:
        comorbidity_index[patient] = sum(comorbidity_index[patient].values())


# patient, sex, birth, age, center, t90_date, t90_years
def write_static_table(name):
    header = ['id_paciente', 'sexo', 'nacimiento', 'edad_2016', 'centro', 'sector', 'fecha_diagnostico',
              'edad_diagnostico', 'anos_con_DM', 'severity_index', 'comorbidity_index']

    report = open(name + '.csv', 'w', newline='')
    wr = csv.writer(report, delimiter=';')
    wr.writerow(header)

    for patient in patients_log:
        line = [patient]
        line += patients_log[patient]
        if len(patients_log[patient]) < 6:
            line += ['s/diagT90', 's/diagT90', 's/diagT90']
        line.append(severity_index[patient])
        line.append(comorbidity_index[patient])

        ''' Esto era para imprimir la severidad y comorbilidad de cada categoria, pero el indice es la suma
        for cat in severity_cat:
            line.append(severity_index_category[patient][cat])
        for cat in comorbidity_cat:
            line.append(comorbidity_index_category[patient][cat])
        '''

        wr.writerow(line)
    report.close()


read_files()
static_patients()
write_static_table('static4')


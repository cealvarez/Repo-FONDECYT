__author__ = 'Tania'

import pandas as pd
from datetime import datetime
import csv
import calendar

# Parameters
center_param = 'X'  # MTC, JPII, SAH, whatever = X
min_number_of_total_tests = 2  # p/patient during he whole period
min_age = 0
max_age = 600

# By default a year is divided in monthly periods
# periods_per_year = 12  # (12/period_per_year months). 12 = monthly (12/12); 2 = biannual (12/2); 4 = quarterly (12/4)
days_per_period = 30

# Dates between which the file is read
starting_year = 2014
starting_month = 1
end_year = 2015
end_month = 9

# Files
# file_cube_explicit_derivation = 'Log/log_hba1c_complete.csv'
file_dm_compensation_t90 = 'Input/dm_compensation_T90.csv'

total_patients = 0

# Relevant data
patients = {}  # {id: [date, hba1c, condition]}
patients_periods = {}  # 'calendar' of patients' months patients_periods[patient][period] = [hba1c, condition]
patients_age = {}
patients_gender = {}


# 08-04-2016
def read_dm_compensation_t90():
    global patients_age
    global patients_gender

    data = pd.read_csv(file_dm_compensation_t90, sep=';')
    data['fecha'] = pd.to_datetime(data['fecha'], format="%Y-%m-%d %H:%M:%S")
    data = data.sort_index(by=['id_paciente', 'fecha'])
    data['fecha'] = data['fecha'].apply(lambda x: x.strftime('%Y-%m-%d'))

    prev_id = 0

    for center, sector, patient, date, hba1c, condition, age, gender in \
            zip(data['centro'], data['sector'], data['id_paciente'], data['fecha'], data['examen_hba1c'],
                data['dm_compensacion'], data['edad_paciente'], data['sexo']):
        if center != center_param and center_param != 'X':
            continue

        if age < min_age or age > max_age:
            continue

        date = datetime.strptime(date, "%Y-%m-%d")
        year = date.year
        month = date.month
        if year < starting_year or year > end_year:
            continue
        elif year == starting_year and month < starting_month:
            continue
        elif year == end_year and month > end_month:
            continue

        if patient != prev_id:
            prev_id = patient
            patients[patient] = []
            patients_age[patient] = age
            patients_gender[patient] = gender
        patients[patient].append([date, float(hba1c), condition])

    # remove patients with very few measurements and save the first and last date for the other patients
    remove_keys = []
    for patient in patients:
        if len(patients[patient]) < min_number_of_total_tests:
            remove_keys.append(patient)
    for key in remove_keys:
        del patients[key]
        del patients_age[key]
        del patients_gender[key]

    return len(patients)


def show_time_between_tests(min_months=1/30, max_months=12):
    # months between tests
    total = 0
    count1 = 0
    count2 = 0
    for patient in patients:
        #print('\n', patient, '\t', end='')
        for index in range(len(patients[patient])-1):
            total += 1
            date1 = patients[patient][index][0]
            date2 = patients[patient][index+1][0]

            condition1 = patients[patient][index][2]
            condition2 = patients[patient][index+1][2]
            # if condition1 < condition2:

            if int((date2-date1).days/30) < min_months:  # and condition1 < condition2:
                #print(int((date2-date1).days/30), '\t', end='')
                count1 += 1
            elif int((date2-date1).days/30) > max_months:  # and condition1 < condition2:
                #print(int((date2-date1).days/30), '\t', end='')
                count2 += 1
    print()
    print('TOTAL: ', total)
    print('TOTAL < ', min_months, ': ', count1, '\t%: ', count1*100/total)
    print('TOTAL > ', max_months, ': ', count2, '\t%: ', count2*100/total)


# OLD
# completes the dictionary with transitions from the original data
def mark_gross_transitions():
    patients_transitions = {}
    for patient in patients:
        patients_transitions[patient] = {'CD': [], 'DC': [], 'CC': [], 'DD': []}
        prev_transition = 0
        first = 0
        last = 0

        for index in range(len(patients[patient])-1):
            test1 = patients[patient][index]
            test2 = patients[patient][index+1]

            if test1[2] < test2[2]:
                transition = 'DC'
            elif test1[2] > test2[2]:
                transition = 'CD'
            elif test1[2] == test2[2] == 1:
                transition = 'CC'
            else:
                transition = 'DD'

            if (transition == 'DD' or transition == 'CC') and transition == prev_transition:
                last = test2[0]
            elif (transition == 'DD' or transition == 'CC') and transition != prev_transition:
                # previous_transition has to be CD or DC, respectively
                first = test1[0]
                last = test2[0]

            if transition == 'CD' or transition == 'DC':
                if first != 0:
                    patients_transitions[patient][prev_transition].append([first, last])
                    first = 0
                    last = 0
                patients_transitions[patient][transition].append([test1[0], test2[0]])
            else:
                if index + 1 == len(patients[patient])-1 and first != 0:
                    patients_transitions[patient][transition].append([first, last])

            prev_transition = transition

    return patients_transitions

    # for patient in patients_transitions:
       # print()
       # print(patient)
       # for transition in patients_transitions[patient]:
            # print(transition, '\t', patients_transitions[patient][transition])
            # print()


# Returns the number of days between two dates, regardless of the time of day
def days_between(d1, d2):
    d1 = datetime.date(d1)
    d2 = datetime.date(d2)

    return abs((d2 - d1).days)


# periods are counted from 0 onwards
def date_to_period_translator(init_date, date):
    days = days_between(init_date, date)

    return int(days/days_per_period)


# relative periods to each patient
def mark_periods():
    graph_list = {}
    for patient in patients:
        init_date = patients[patient][0][0]
        last_date = patients[patient][len(patients[patient])-1][0]
        periods = date_to_period_translator(init_date, last_date)
        patients_periods[patient] = [None for i in range(periods+1)]
        graph_list[patient] = [[] for i in range(2)]
        for test in patients[patient]:
            date = test[0]
            hba1c = test[1]
            condition = test[2]

            period = date_to_period_translator(init_date, date)

            # Altered condition predominates over not altered condition
            if condition == 1 and patients_periods[patient][period] is not None:
                continue
            patients_periods[patient][period] = [hba1c, condition]

            graph_list[patient][0].append(period)
            graph_list[patient][1].append(test[1])

    return graph_list


def write_calendar(detail, max_months):
    calendar = open('Log/new/calendar_' + detail + '_' + center_param + '.csv', 'w', newline='')
    wr = csv.writer(calendar, delimiter=';')
    header = []
    for i in range(max_months):
        header.append('mes ' + str(i))
    header.append(None)
    header.append('id_paciente')
    wr.writerow(header)
    for patient in patients_periods:
        line = []
        for period in range(max_months):
            if period < len(patients_periods[patient]):
                if patients_periods[patient][period] is not None:
                    line.append(patients_periods[patient][period][1])
                else:
                    line.append(None)
            else:
                line.append(None)
        line.append(None)
        line.append(patient)
        wr.writerow(line)
    calendar.close()


# Compensation rules:
# 1) A decompensated patient stays that way until he/she has a balanced examination
# 2) A patient is compensated for 6 months from the examination unless another test says otherwise during that period
def apply_compensation_rules():
    max_months = 0
    for patient in patients:
        for index in range(len(patients[patient])):
            date = patients[patient][index][0]
            condition = patients[patient][index][2]
            init_date = patients[patient][0][0]
            period = date_to_period_translator(init_date, date)
            i = 1
            if condition == 1:
                while i < 6:
                    if period+i >= len(patients_periods[patient]):
                        patients_periods[patient].append(None)
                    else:
                        if patients_periods[patient][period+i] is not None:
                            break
                    patients_periods[patient][period+i] = [-1, 'C']
                    i += 1

            else:  # condition == 0
                while period+i < len(patients_periods[patient]) or i < 6:
                    if period+i == len(patients_periods[patient]):
                        patients_periods[patient].append(None)
                    if patients_periods[patient][period+i] is None:
                        patients_periods[patient][period+i] = [-1, 'D']
                    else:
                        break
                    i += 1
        max_months = max(max_months, len(patients_periods[patient]))

    return max_months


# ACTUALIZAR
def search_cases_dc(decompensation_window_DC, patients_transitions):  # decompensation_window_DC = 12 (months)
    graph_list = {}
    total = 0
    last = 0
    for patient in patients_periods:
        count = 0
        graph_x = []
        graph_y = []
        for period in range(len(patients_periods[patient])-1):
            status = patients_periods[patient][period]
            if status is not None and (status[1] == 0 or status[1] == 'D'):
                count += 1
                last = period
                if status[1] == 0:
                    graph_x.append(period)
                    graph_y.append(patients_periods[patient][period][0])
            else:
                if count >= decompensation_window_DC:
                    if patient not in patients_transitions:
                        patients_transitions[patient] = {}
                    if 'DC' not in patients_transitions[patient]:
                        patients_transitions[patient]['DC'] = []
                    total += 1
                    first = period_to_dates_translator(period - decompensation_window_DC)[0]
                    last = period_to_dates_translator(last)[1]
                    patients_transitions[patient]['DC'].append([first, last])

                    graph_x.append(period)
                    graph_y.append(float(patients_periods[patient][period][0]))
                    graph_list[patient] = [[] for i in range(2)]
                    graph_list[patient][0] = graph_x
                    graph_list[patient][1] = graph_y

                count = 0
                last = 0
                graph_x = []
                graph_y = []
    # print('TOTAL CASES: ', total)
    tot = 0
    for patient in patients_transitions:
        if len(patients_transitions[patient]['DC']) > 0:
            tot += 1
            print()
            print(patient)
            print('DC', '\t', patients_transitions[patient]['DC'])
            print()
    print('TOTAL CASES: ', total, '\nTOTAL PATIENTS: ', tot)

    return graph_list

# ACTUALIZAR
def search_cases_dd(patients_transitions):
    total = 0
    last = 0
    graph_list = {}

    for patient in patients_periods:
        count = 0
        graph_x = []
        graph_y = []
        for period in range(len(patients_periods[patient])):
            status = patients_periods[patient][period]
            if status is not None and (status[1] == 0 or status[1] == 'D'):
                count += 1
                last = period
                if status[1] == 0:
                    graph_x.append(period)
                    graph_y.append(float(patients_periods[patient][period][0]))

            else:
                count = 0
                break
        if count > 0:
            total += 1
            first = period_to_dates_translator(0)[0]
            last = period_to_dates_translator(last)[1]

            if patient not in patients_transitions:
                patients_transitions[patient] = {}
            if 'DD' not in patients_transitions[patient]:
                patients_transitions[patient]['DD'] = []
            patients_transitions[patient]['DD'].append([first, last])

            graph_list[patient] = [[] for i in range(2)]
            graph_list[patient][0] = graph_x
            graph_list[patient][1] = graph_y

    print('TOTAL CASES: ', total)
    for patient in patients_transitions:
        if len(patients_transitions[patient]['DD']) > 0:
            print()
            print(patient)
            print('DD', '\t', patients_transitions[patient]['DD'])
            print()

    return graph_list


def set_data():
    read_dm_compensation_t90()
    mark_periods()
    apply_compensation_rules()

    return patients, patients_periods, patients_age, patients_gender


#set_data()
#graph_list = search_cases_dd(patients_transitions={})






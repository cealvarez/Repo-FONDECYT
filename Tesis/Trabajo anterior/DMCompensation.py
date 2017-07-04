__author__ = 'Tania'

import Reader
from datetime import datetime
import csv

# This file analyze data about hba1c measurements

# Parameters

# By default a year is divided in monthly periods
days_per_period = 30

# Relevant data
patients = {}  # {id: [date, hba1c, condition]}
patients_periods = {}  # 'calendar' of patients' months patients_periods[patient][period] = [hba1c, condition]
patients_periods_rules = {}  # 'calendar' considering rules for compensation (CC: 6 months, etc...)


def set_only_dm_data(clusters_file, clusters, dm_file, center_param, min_age, max_age, start, finish, min_number_of_total_tests):
    global patients
    Reader.read_clusters(clusters_file, clusters)
    patients = Reader.read_dm_compensation_t90(dm_file, center_param, min_age, max_age, start, finish,
                                               min_number_of_total_tests)


# FALTA ACTUALIZARLO (lea clusters)
def show_time_between_tests(min_months=1/30, max_months=12):
    # months between tests
    total = 0
    count1 = 0
    count2 = 0
    for patient in patients:
        print('\n', patient, '\t', end='')
        for index in range(len(patients[patient])-1):
            total += 1
            date1 = patients[patient][index][0]
            date2 = patients[patient][index+1][0]

            condition1 = patients[patient][index][2]
            condition2 = patients[patient][index+1][2]
            # if condition1 < condition2:

            if int((date2-date1).days/30) < min_months:  # and condition1 < condition2:
                print(int((date2-date1).days/30), '\t', end='')
                count1 += 1
            elif int((date2-date1).days/30) > max_months:  # and condition1 < condition2:
                print(int((date2-date1).days/30), '\t', end='')
                count2 += 1
    print()
    print('TOTAL: ', total)
    print('TOTAL < ', min_months, ': ', count1, '\t%: ', count1*100/total)
    print('TOTAL > ', max_months, ': ', count2, '\t%: ', count2*100/total)


# returns the number of days between two dates, regardless of the time of day
def days_between(d1, d2):
    d1 = datetime.date(d1)
    d2 = datetime.date(d2)

    return abs((d2 - d1).days)


# periods are counted from 0 onwards
def date_to_period_translator(init_date, date):
    days = days_between(init_date, date)

    return int(days/days_per_period)


# to each cluster: define relative periods to each patient (each patient has her own init_date)
# marks the value for each measurement in the corresponding period and returns the list of points
# X: period; Y: measurement
def mark_periods():
    global patients_periods
    graph_list = {}
    for cluster in patients:
        patients_periods[cluster] = {}
        graph_list[cluster] = {}
        for patient in patients[cluster]:
            init_date = patients[cluster][patient][0][0]
            last_date = patients[cluster][patient][len(patients[cluster][patient])-1][0]
            periods = date_to_period_translator(init_date, last_date)
            patients_periods[cluster][patient] = [None for i in range(periods+1)]
            graph_list[cluster][patient] = [[] for i in range(2)]
            for test in patients[cluster][patient]:
                date = test[0]
                hba1c = test[1]
                condition = test[2]

                period = date_to_period_translator(init_date, date)

                # Altered condition predominates over not altered condition
                if condition == 1 and patients_periods[cluster][patient][period] is not None:
                    continue
                patients_periods[cluster][patient][period] = [hba1c, condition]

                graph_list[cluster][patient][0].append(period)
                graph_list[cluster][patient][1].append(hba1c)

    return graph_list


def write_calendar(detail, max_months, center_param, cluster):
    calendar = open('Log/new/calendar_' + detail + '_' + center_param + '_' + cluster + '.csv', 'w', newline='')
    wr = csv.writer(calendar, delimiter=';')
    header = []
    for i in range(max_months):
        header.append('mes ' + str(i))
    header.append(None)
    header.append('id_paciente')
    wr.writerow(header)
    for patient in patients_periods[cluster]:
        line = []
        for period in range(max_months):
            if period < len(patients_periods[cluster][patient]):
                if patients_periods[cluster][patient][period] is not None:
                    line.append(patients_periods[cluster][patient][period][1])
                else:
                    line.append(None)
            else:
                line.append(None)
        line.append(None)
        line.append(patient)
        wr.writerow(line)
    calendar.close()


# Compensation rules:
# 1) A altered ('bad') patient stays that way until he/she has a balanced examination
# 2) A patient is compensated for 6 months from the examination unless another test says otherwise during that period
def apply_compensation_rules():
    max_months = 0
    for cluster in patients:
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
    graph_list = mark_periods()
    apply_compensation_rules()

    return patients, patients_periods, patients_age, patients_gender, graph_list

# set_data()
# graph_list = search_cases_dd(patients_transitions={})






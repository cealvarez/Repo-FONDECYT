# Log Structure: case | timestamp | activity | executor | estate | center | others...
def read_log(log_file, start, finish, cv_frequency):
    print("READ LOG\n")

    # Key: cluster. Value: list of patients with their appointments
    log_patients = {}

    # Key: Patient. Value: dictionary with Key: Activity and Value: frequency
    patient_act_frequency = {}

    # patient: cluster
    patient_cluster = {}

    data = pd.read_csv(log_file, sep=';')
    data['fecha'] = pd.to_datetime(data['fecha'], format="%d-%m-%Y")
    data = data.sort_index(by=['id_paciente', 'fecha'])
    data['fecha'] = data['fecha'].apply(lambda x: x.strftime('%d/%m/%Y'))

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
    professional_number_list = {}

    ###FILA 80525 PACIENTE 14002 20114/06/18 NO TIENE ESTAMENTO
    writer = open('Log/log-detailed.csv', 'w')
    #for period, patient, timestamp, act, executor, estate, relevant, estate_to, next_month in \
    #        zip(data['id_caso'], data['id_paciente'], data['fecha'], data['actividad'], data['medico_id'], data['medico_estamento'],
    #            data['relevante'], data['derivado'], data['mes']):

    for patient, timestamp, act, executor, estate, relevant, estate_to, next_month in \
            zip(data['id_paciente'], data['fecha'], data['actividad'], data['medico_id'], data['medico_estamento'],
                data['relevante'], data['derivado'], data['mes'], data['ciap'], data['severidad'], data['comorbilidad'], 
                data['fecha_diagnostico'], data['tiempo_diab'], data['centro'], data['sector'], data['actividad_simplificada'], 
                data['actividad_muy_simplificada'], data['hba1c']):

        if relevant == 'NO':
            continue

        if estate == 'LABORATORIO':
            continue

        time = datetime.strptime(timestamp, "%d/%m/%Y")
        appoint_date = time

        #if act not in valid_acts:
        #    continue
        #if patient not in patient_cluster:
        #    continue

        
        #cluster = patient_cluster[patient]
        #if cluster not in log_patients:
            #log_patients[cluster] = {}
            #act_freq[cluster] = {}
            #estate_freq[cluster] = {}
            #professional_freq[cluster] = {}
            #estate_professionals[cluster] = {}
            #patients_cv[cluster] = {}
            #next_appointment[cluster] = {}
            #patient_professionals[cluster] = {}
            #patient_activities[cluster] = {}
            #professional_number_in_patient[cluster] = {}

        #patients_list = log_patients[cluster]
        #acts_list = act_freq[cluster]
        #professionals_list = professional_freq[cluster]
        #estates_list = estate_freq[cluster]
        #estate_prof_list = estate_professionals[cluster]
        #patients_cv_list = patients_cv[cluster]
        #patient_professionals_list = patient_professionals[cluster]
        #patient_activities_list = patient_activities[cluster]
        #professional_number_list = professional_number_in_patient[cluster]
        #event = Appointment(patient, time, act, period, executor, estate, 0)
        event = Appointment(patient, time, act, 1, executor, estate, 0)
        
        #if estate_to != estate_to:
        #    estate_to = 'ANY'
        #if next_month != next_month:
        #    next_month = 0        
                
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

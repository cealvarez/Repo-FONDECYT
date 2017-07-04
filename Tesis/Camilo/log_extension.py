import pandas as pd
from datetime import datetime

def read_log(log_file):

    data = pd.read_csv(log_file, sep=';')
    #data['fecha_inicio'] = pd.to_datetime(data['fecha'], format="%d-%m-%y %H:%M")
    #data = data.sort_index(by=['id_paciente', 'fecha'])
    #data['fecha'] = data['fecha'].apply(lambda x: x.strftime('%d/%m/%y'))

    case = ""
    year_case = ""
    profs = []
    professional_number_list = {}
    annual_professional_number_list = {}
    for patient, start, end, executor, estate in \
            zip(data['id_paciente'], data['fecha_inicio'], data['fecha_fin'], data['medico_id'], data['medico_estamento']):

        if estate == 'LABORATORIO' or estate == 'SIM' or estate == 'TECNICO_PARAMEDICO':
            continue

        year = datetime.strptime(start, "%d-%m-%y %H:%M").year % 100
                
        if estate not in profs:
            profs.append(estate)

        if case == '':
            case = str(patient)
            year_case = year
            med_count = 1
            enf_count = 1
            nut_count = 1
            kin_count = 1
            mat_count = 1
            odo_count = 1
            psi_count = 1
            asi_count = 1

            annual_med_count = 1
            annual_enf_count = 1
            annual_nut_count = 1
            annual_kin_count = 1
            annual_mat_count = 1
            annual_odo_count = 1
            annual_psi_count = 1
            annual_asi_count = 1
        elif case != str(patient):
            year_case = year
            case = str(patient)
            med_count = 1
            enf_count = 1
            nut_count = 1
            kin_count = 1
            mat_count = 1
            odo_count = 1
            psi_count = 1
            asi_count = 1

            annual_med_count = 1
            annual_enf_count = 1
            annual_nut_count = 1
            annual_kin_count = 1
            annual_mat_count = 1
            annual_odo_count = 1
            annual_psi_count = 1
            annual_asi_count = 1

        if year != year_case:
            year_case = year
            annual_med_count = 1
            annual_enf_count = 1
            annual_nut_count = 1
            annual_kin_count = 1
            annual_mat_count = 1
            annual_odo_count = 1
            annual_psi_count = 1
            annual_asi_count = 1

        if case not in professional_number_list:
            professional_number_list[case] = {}
            annual_professional_number_list[case] = {}
        if year not in annual_professional_number_list[case]:
            annual_professional_number_list[case][year] = {}
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
            if estate == 'KINESIOLOGO':
                professional_number_list[case][executor] = 'KINESIOLOGO ' + str(kin_count)
                kin_count += 1
            if estate == 'MATRON(A)':
                professional_number_list[case][executor] = 'MATRON(A) ' + str(mat_count)
                mat_count += 1
            if estate == 'ODONTOLOGO':
                professional_number_list[case][executor] = 'ODONTOLOGO ' + str(odo_count)
                odo_count += 1
            if estate == 'PSICOLOGO-A':
                professional_number_list[case][executor] = 'PSICOLOGO-A ' + str(psi_count)
                psi_count += 1
            if estate == 'ASISTENTE_SOCIAL':
                professional_number_list[case][executor] = 'ASISTENTE_SOCIAL ' + str(asi_count)
                asi_count += 1

        if executor not in annual_professional_number_list[case][year]:
            if estate == 'MEDICO':
                annual_professional_number_list[case][year][executor] = 'MEDICO ' + str(annual_med_count)
                annual_med_count += 1
            if estate == 'ENFERMERA':
                annual_professional_number_list[case][year][executor] = 'ENFERMERA ' + str(annual_enf_count)
                annual_enf_count += 1
            if estate == 'NUTRICIONISTA':
                annual_professional_number_list[case][year][executor] = 'NUTRICIONISTA ' + str(annual_nut_count)
                annual_nut_count += 1
            if estate == 'KINESIOLOGO':
                annual_professional_number_list[case][year][executor] = 'KINESIOLOGO ' + str(annual_kin_count)
                annual_kin_count += 1
            if estate == 'MATRON(A)':
                annual_professional_number_list[case][year][executor] = 'MATRON(A) ' + str(annual_mat_count)
                annual_mat_count += 1
            if estate == 'ODONTOLOGO':
                annual_professional_number_list[case][year][executor] = 'ODONTOLOGO ' + str(annual_odo_count)
                annual_odo_count += 1
            if estate == 'PSICOLOGO-A':
                annual_professional_number_list[case][year][executor] = 'PSICOLOGO-A ' + str(annual_psi_count)
                annual_psi_count += 1
            if estate == 'ASISTENTE_SOCIAL':
                annual_professional_number_list[case][year][executor] = 'ASISTENTE_SOCIAL ' + str(annual_asi_count)
                annual_asi_count += 1


    reader = open('log_ctcv.csv', 'r')
    writer = open('log_estamentos.csv', 'w')
    #print(reader.readline().strip() + ";estate_number\n")
    writer.write(reader.readline().strip() + ";numero_estamento;numero_estamento_anual\n")
    for line in reader:
        pat = line.strip().split(";")[0]
        estate = line.strip().split(";")[3]
        if estate == 'LABORATORIO' or estate == 'SIM' or estate == 'TECNICO_PARAMEDICO':
            estate_number = "none"
            annual_estate_number = "none"
        else:
            year = int(line.strip().split(";")[1][6:8])
            execut = line.strip().split(";")[4]
            estate_number = professional_number_list[pat][execut]
            annual_estate_number = annual_professional_number_list[pat][year][execut]
        writer.write(line.strip() + ";" + estate_number + ";" + annual_estate_number + "\n")
    writer.close()

read_log('log_ctcv.csv')

from datetime import datetime, timedelta

reader = open("report_log_adherencia_V4.csv", "r")
writer = open("transition_log_V4.csv", "w")

report = open("report_interruption.csv", "w")
report.write("paciente;secuencia;nodos X;nodos O;duracion X;duracion O;Proporcion grupo\n")

reader.readline()
patient_dic = {}

lineal_label = "Delegador"
lineal_auto_label = "Deleg. reasig."
derivation_label = "Der. Ciclica"
collaboration_label = "Contraderivacion"
hybrid_label = "Contraderivacion"
star_label = "Particip. Coord"
sin_tipo_label = "sin_tipo"

times_matter = False
sin_tipo = True

for line in reader:
    lista = line.strip().split(';')
    patient = lista[1]
    start = lista[2]
    end = lista[3]
    type = lista[8]
    number = lista[9]

    if patient not in patient_dic:
        new = True
        diff = 0
        patient_dic[patient] = []

    if type in [collaboration_label, hybrid_label, derivation_label]:
        if new:
            new = False
            diff = int(number) - 1
            number = "1"
        else:
            number = str(int(number) - diff)
    elif type in [lineal_auto_label, lineal_label, star_label]:
        number = ""
    else:
        if sin_tipo:
            number = ""
        else:
            continue

    if len(patient_dic[patient]) > 0:
        last = patient_dic[patient][-1]
        if last[0] != type or last[1] != number:
            patient_dic[patient].append([type, number, start, end])
        else:
            last[3] = end
    else:
        patient_dic[patient].append([type, number, start, end])

corrected_treatment = {}
###########################FALTA CONSIDERAR TIEMPO DE TRANSICION ENTRE DOS GRUPOS

for p in patient_dic:
    t = patient_dic[p]
    #print(t)
    maybe_interrupted = False
    interrupted = False
    maybe_casual = True
    casual = False
    pattern_index = -1
    last_index = -1
    treatment_list = []
    for i in range(len(t)):
        if t[i][0] in [collaboration_label, hybrid_label, derivation_label, star_label]:
            if last_index == -1:
                pattern_index = i
            last_index = i
            treatment_list.append(1)
        else:
            treatment_list.append(0)

    if sum(treatment_list) == len(treatment_list): #puras colaboraciones
        corrected_treatment[p] = [["Participativo", "", t[pattern_index][2], t[last_index][3]]]
    elif sum(treatment_list) == 0: ##puras delegaciones
        pass
    else:
        #print(treatment_list)
        s = ""
        x_time_count = 0
        x_node_count = 0
        o_time_count = 0
        o_node_count = 0
        for i in range (len(treatment_list)):
            if treatment_list[i] == 0:
                s += "X"
                x_node_count += 1
                x_time_count += (datetime.strptime(t[i][3], "%d-%m-%y %H:%M") - datetime.strptime(t[i][2], "%d-%m-%y %H:%M")).days
            else:
                s += "O"
                o_node_count += 1
                o_time_count += (datetime.strptime(t[i][3], "%d-%m-%y %H:%M") - datetime.strptime(t[i][2], "%d-%m-%y %H:%M")).days

            if i < len(treatment_list) - 1:
                x_time_count += (datetime.strptime(t[i+1][2], "%d-%m-%y %H:%M") - datetime.strptime(t[i][3], "%d-%m-%y %H:%M")).days

        time_in_group_treatment = o_time_count/(o_time_count + x_time_count)
        report.write(p + ";" + s + ';' + str(x_node_count) + ';' + str(o_node_count) + ';' + str(x_time_count) + ';' + str(o_time_count) + ';' + str(time_in_group_treatment) + '\n')

        if s in ['XO', 'OX'] and time_in_group_treatment > 0.9:
            #print(p, t)
            continue

        if time_in_group_treatment > 0.7:
            corrected_treatment[p] = [["Participativo", "", t[pattern_index][2], t[last_index][3]]]

        elif time_in_group_treatment > 0.3:
            #if 'OO' in s:
            #    corrected_treatment[p] = [["Interr conj", "", t[pattern_index][2], t[last_index][3]]]
            #else:
                corrected_treatment[p] = [["Interr", "", t[pattern_index][2], t[last_index][3]]]

        else:
            corrected_treatment[p] = [["Casual", "", t[pattern_index][2], t[last_index][3]]]
###########################



writer.write("id_paciente;id_paciente;transicion;fecha_inicio;fecha_fin\n")
for p in patient_dic:
    if p not in corrected_treatment:
        for i in range (len(patient_dic[p])):
            t = patient_dic[p][i]
            if (i == 0 or i == len(patient_dic[p]) - 1) and t[0] == "sin_tipo":
                continue
            if times_matter:
                writer.write(p + ';' + p + ';' + t[0] + t[1] + ';' + t[2]+ ';' + t[3] + '\n')
            else:
                writer.write(p + ';' + p + ';' + t[0] + ';' + t[2]+ ';' + t[3] + '\n')
    else:
        t = corrected_treatment[p][0]
        writer.write(p + ';' + p + ';' + t[0] + ';' + t[2]+ ';' + t[3] + '\n')
reader.close()
writer.close()
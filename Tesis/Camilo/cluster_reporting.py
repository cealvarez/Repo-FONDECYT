reader = open("transition_log_V4.csv", "r")
writer = open("cluster.csv", "w")
patient_treatments = {}

reader.readline()
for line in reader:
    lista = line.strip().split(';')
    patient = lista[0]
    treatment = lista[2]
    if patient not in patient_treatments:
        patient_treatments[patient] = []
    if treatment not in patient_treatments[patient]:
        patient_treatments[patient].append(treatment)

writer.write('paciente;cluster\n')
for p in patient_treatments:
    if len(patient_treatments[p]) == 1:
        writer.write(p + ";" + patient_treatments[p][0] + "\n")
    elif len(patient_treatments[p]) == 2:
        if "Colaboracion" in patient_treatments[p] and "cascada_auto" in patient_treatments[p]:
            writer.write(p + ";colaboracion_semiauto\n")
        elif "Derivacion" in patient_treatments[p] and "cascada_auto" in patient_treatments[p]:
            writer.write(p + ";derivacion_semiauto\n")
        elif "Colaboracion" in patient_treatments[p] and "cascada" in patient_treatments[p]:
            writer.write(p + ";colaboracion_semi\n")
        else:
            writer.write(p + ";outlier\n")
    else:
        writer.write(p + ";outlier\n")

reader.close()
writer.close()
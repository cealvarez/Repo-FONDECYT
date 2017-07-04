reader = open("log_adherencia.csv", 'r')
writer = open("report_adherence.csv", 'w')
reader.readline()
writer.write('id_paciente;adherencia\n')
adherence_dic = {}
p = -1
effective = 0
total = 0
for line in reader:
    lista = line.strip().split(';')
    patient = lista[1]
    value = int(lista[11])
    if p == -1:
        p = patient
    elif p != patient:
        if total > 0:
            adherence_dic[p] = round(effective/total, 2)
        p = patient
        effective = 0
        total = 0
    if value > -1:
        total += 1
        effective += value
if total > 0:
    adherence_dic[p] = round(effective/total, 2)
for p in adherence_dic:
    writer.write(p + ";" + str(adherence_dic[p]) + "\n")

reader.close()
writer.close()
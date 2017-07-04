from datetime import datetime, timedelta

reader = open("transition_log_V4.csv", "r")
writer = open("resource_report.csv", "w")
reader.readline()
writer.write("id_paciente;transicion;medicos;enfermeras;nutricionistas\n")
dic = {}
for line in reader:
    lista = line.strip().split(';')
    t = (lista[2],datetime.strptime(lista[3], "%d-%m-%y %H:%M"),datetime.strptime(lista[4], "%d-%m-%y %H:%M"))
    dic[lista[0]] = t
reader.close()
reader = open("report_log_estamentos_V3.csv", "r")
reader.readline()
prof_dic = {}
for line in reader:
    lista = line.strip().split(';')
    p = lista[1]
    if p in dic:
        if p not in prof_dic:
            prof_dic[p] = {}
            prof_dic[p]["MEDICO"] = []
            prof_dic[p]["ENFERMERA"] = []
            prof_dic[p]["NUTRICIONISTA"] = []
        start = datetime.strptime(lista[2], "%d-%m-%y %H:%M")
        if dic[p][1] <= start <= dic[p][2]:
            estate = lista[4]
            person = lista[5]
            if person not in prof_dic[p][estate]:
                prof_dic[p][estate].append(person)
for p in prof_dic:
    writer.write(p + ";" + dic[p][0] + ";" + str(len(prof_dic[p]["MEDICO"])) + ";" + str(len(prof_dic[p]["ENFERMERA"])) + ";"
                 + str(len(prof_dic[p]["NUTRICIONISTA"])) + "\n")

reader.close()
writer.close()

from datetime import datetime, timedelta

reader = open("transition_log_V5.csv", "r")
writer = open("resource_report_V2.csv", "w")
reader.readline()
writer.write("id_paciente;transicion;medicos;enfermeras;nutricionistas;medicos NC;enfermeras NC;nutricionistas NC\n")
dic = {}
for line in reader:
    lista = line.strip().split(';')
    t = (lista[2],datetime.strptime(lista[3], "%d-%m-%y %H:%M"),datetime.strptime(lista[4], "%d-%m-%y %H:%M"))
    dic[lista[0]] = t
reader.close()
reader = open("report_log_adherencia_V4.csv", "r")
reader.readline()
prof_dic = {}

non_colaborative = "_NC"
lineal_label = "Delegador"
lineal_auto_label = "Deleg. reasig."
derivation_label = "Der. Ciclica"
collaboration_label = "Contraderivacion"
hybrid_label = "Contraderivacion"
star_label = "Particip. Coord"
sin_tipo_label = "sin_tipo"

for line in reader:
    lista = line.strip().split(';')
    p = lista[1]
    segment = lista[8]
    if p in dic:
        if p not in prof_dic:
            prof_dic[p] = {}
            prof_dic[p]["MEDICO"] = []
            prof_dic[p]["ENFERMERA"] = []
            prof_dic[p]["NUTRICIONISTA"] = []
            prof_dic[p]["MEDICO" + non_colaborative] = []
            prof_dic[p]["ENFERMERA" + non_colaborative] = []
            prof_dic[p]["NUTRICIONISTA" + non_colaborative] = []
        start = datetime.strptime(lista[2], "%d-%m-%y %H:%M")
        #if dic[p][1] <= start <= dic[p][2]:
        estate = lista[4]
        person = lista[5]
        if segment in [sin_tipo_label, lineal_auto_label, lineal_label]:
            if person not in prof_dic[p][estate + non_colaborative]:
                prof_dic[p][estate + non_colaborative].append(person)
        else:
            if person not in prof_dic[p][estate]:
                prof_dic[p][estate].append(person)
for p in prof_dic:
    writer.write(p + ";" + dic[p][0] + ";" + str(len(prof_dic[p]["MEDICO"])) + ";" + str(len(prof_dic[p]["ENFERMERA"])) + ";"
                 + str(len(prof_dic[p]["NUTRICIONISTA"])) + ";" + str(len(prof_dic[p]["MEDICO" + non_colaborative])) + ";"
                 + str(len(prof_dic[p]["ENFERMERA" + non_colaborative])) + ";" + str(len(prof_dic[p]["NUTRICIONISTA" + non_colaborative])) + "\n")

reader.close()
writer.close()

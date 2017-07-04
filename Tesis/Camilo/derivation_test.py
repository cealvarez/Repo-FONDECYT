from datetime import datetime, timedelta

#new_time = datetime.strptime(time, "%d-%m-%y %H:%M")
#new_time = new_time + timedelta(minutes = 1)
#new_time_finish = new_time + timedelta(minutes = 1)
#patient_dic[patient][time][3][ciap] = (new_time.strftime("%d-%m-%y %H:%M"), new_time_finish.strftime("%d-%m-%Y %H:%M"))


reader = open("report_log_estamentos_V3.csv", "r")
writer = open("collaboration_report.csv", "w")

reader.readline()
writer.write("number;time\n")
line = reader.readline()
event = 1
while line != "":
    lista = line.strip().split(';')
    paciente = lista[1]
    tipo = lista[8]
    numero = lista[9]
    p1 = lista[5]
    start = datetime.strptime(lista[2], "%d-%m-%y %H:%M")
    if tipo == "Subcon. simple":
        count = 0
        line = reader.readline()
        lista2 = line.strip().split(';')
        paciente2 = lista2[1]
        tipo2 = lista2[8]
        numero2 = lista2[9]
        p2 = lista2[5]
        start2 = datetime.strptime(lista2[2], "%d-%m-%y %H:%M")
        while paciente == paciente2 and tipo == tipo2 and numero2 == numero:
            if p2 != p1:
                count += 1
                p1 = p2
            time_difference = round((start2 - start).days/365, 2)
            line = reader.readline()
            lista2 = line.strip().split(';')
            paciente2 = lista2[1]
            tipo2 = lista2[8]
            numero2 = lista2[9]
            p2 = lista2[5]
            start2 = datetime.strptime(lista2[2], "%d-%m-%y %H:%M")
        writer.write(str(paciente) + " " + str(count) + ";" + str(time_difference) + "\n")
        event += 1
    else:
        line = reader.readline()
reader.close()
writer.close()
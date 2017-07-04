from datetime import datetime, timedelta

reader = open("log_estamentos.csv", "r")
cube = open("referrals.csv", "r")
writer = open("log_adherencia.csv", "w")
writer.write(reader.readline().strip() + ";a_tiempo\n")

referrals = {}
cube.readline()
for line in cube:
    lista = line.strip().split(';')
    tupla = (lista[0], lista[1])
    if lista[5] != "#N/A":
        referrals[tupla] = int(lista[5])

cube.close()

last_patient = ""
next_date_deadline = -1
for line in reader:
    lista = line.strip().split(';')
    paciente = lista[2]
    if lista[0] == "91":
        asdasd = 1
    fecha = lista[4]
    tupla = (paciente, fecha)
    vino = "0"
    if tupla in referrals:
        t1 = datetime.strptime(fecha, "%d-%m-%y %H:%M")
        if last_patient == "" or last_patient != paciente:
            vino = "1"
            last_patient = paciente
        else:
            if t1 < next_date_deadline:
                vino = "1"
            else:
                vino = "0"
        month = referrals[tupla]
        yy = t1.year
        mm = t1.month
        if mm <= month:
            year = yy
        else:
            year = yy + 1
        if month < 9:
            next_date_deadline = datetime.strptime("01-0"+str(month+1)+"-"+str(year), "%d-%m-%Y") + timedelta(days=120)
        elif month < 12:
            next_date_deadline = datetime.strptime("01-"+str(month+1)+"-"+str(year), "%d-%m-%Y") + timedelta(days=120)
        else:
            next_date_deadline = datetime.strptime("01-01-"+str(year), "%d-%m-%Y") + timedelta(days=120)

    else:
        vino = "-1"

    lista.append(vino)
    writer.write(";".join(lista) + "\n")

reader.close()
writer.close()
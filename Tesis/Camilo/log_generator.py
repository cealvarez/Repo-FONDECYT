from datetime import datetime, timedelta
reader = open("log_final.csv", "r")
writer = open("log_ctcv.csv", "w")
reader.readline()
writer.write("id_paciente;fecha_inicio;fecha_fin;medico_estamento;medico_id\n")
for line in reader:
    line = line.replace('"', "")
    lista = line.strip().split(',')
    if lista[1] == 'T90' and lista[9] == 'CTCV' and lista[7] != "ADMINISTRATIVO":
        time = lista[3]
        start = datetime.strptime(time, "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%y %H:%M")
        new_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        new_time = new_time + timedelta(minutes = 1)
        finish = new_time.strftime("%d-%m-%y %H:%M")
        writer.write(str(lista[2]) + ';' + start + ';' + finish + ';' + lista[7] + ';' + lista[8] + '\n')

reader.close()
writer.close()



from datetime import datetime, timedelta

patient_dic = {}
patient_prof = {}
patient_people = {}

reader = open("log_estamentos.csv", "r")
header = reader.readline()
for line in reader:
	lista = line.strip().split(";")
	patient = lista[0]
	if patient not in patient_dic:
		patient_dic[patient] = {}
	if patient not in patient_prof:
		patient_prof[patient] = {}
	if patient not in patient_people:
		patient_people[patient] = {}
	
	time = lista[1]
	time_finish = lista[2]
	ciap = lista[5]
	if time not in patient_dic[patient]:
		patient_dic[patient][time] = [time_finish, lista[3], lista[4], {ciap: (time, time_finish)}, lista[6]]
	else:
		if (ciap not in patient_dic[patient][time][3].keys()):
			new_time = datetime.strptime(time, "%d-%m-%Y %H:%M")
			new_time = new_time + timedelta(minutes = 1)
			new_time_finish = new_time + timedelta(minutes = 1)
			patient_dic[patient][time][3][ciap] = (new_time.strftime("%d-%m-%Y %H:%M"), new_time_finish.strftime("%d-%m-%Y %H:%M"))
		#else:
		#	patient_dic[patient][time] = [lista[2], lista[3], lista[4], ciap + "++", lista[6]]
	
	estamento = lista[3]
	med_id = lista[4]
	if time not in patient_prof[patient]:
		patient_prof[patient][time] = {}
		patient_people[patient][time] = {}
		if ciap not in patient_prof[patient][time]:
			patient_prof[patient][time][ciap] = [estamento]
			patient_people[patient][time][ciap] = [med_id]

	else:
		if ciap not in patient_prof[patient][time]:
			patient_prof[patient][time][ciap] = [estamento]
			patient_people[patient][time][ciap] = [med_id]

		else:
			if med_id not in patient_people[patient][time][ciap]:
				patient_prof[patient][time][ciap].append(estamento)
				patient_people[patient][time][ciap].append(med_id)

reader.close()

for p in patient_prof:
	for t in patient_prof[p]:
		patient_dic[p][t][4] = ""
		for c in patient_prof[p][t]:
			patient_dic[p][t][4] += "_" + c
			if "MEDICO" in patient_prof[p][t][c]:
				patient_dic[p][t][4] += "_"  + "M"*patient_prof[p][t][c].count("MEDICO")
			if "ENFERMERA" in patient_prof[p][t][c]:
				patient_dic[p][t][4] += "_"  + "E"*patient_prof[p][t][c].count("ENFERMERA")
			if "NUTRICIONISTA" in patient_prof[p][t][c]:
				patient_dic[p][t][4] += "_"  + "N"*patient_prof[p][t][c].count("NUTRICIONISTA")
			if "KINESIOLOGO" in patient_prof[p][t][c]:
				patient_dic[p][t][4] += "_"  + "K"*patient_prof[p][t][c].count("KINESIOLOGO")
			if "MATRON(A)" in patient_prof[p][t][c]:
				patient_dic[p][t][4] += "_"  + "MA"*patient_prof[p][t][c].count("MATRON(A)")
			if "ODONTOLOGO" in patient_prof[p][t][c]:
				patient_dic[p][t][4] += "_"  + "O"*patient_prof[p][t][c].count("ODONTOLOGO")
			if "ASISTENTE_SOCIAL" in patient_prof[p][t][c]:
				if (p == "37116"):
					print(patient_prof[p][t])
				patient_dic[p][t][4] += "_"  + "A"*patient_prof[p][t][c].count("ASISTENTE_SOCIAL")
			if "PSICOLOGO-A" in patient_prof[p][t][c]:
				patient_dic[p][t][4] += "_"  + "P"*patient_prof[p][t][c].count("PSICOLOGO-A")
			if "LABORATORIO" in patient_prof[p][t][c]:
				patient_dic[p][t][4] += "_"  + "L"*patient_prof[p][t][c].count("LABORATORIO")
			if "TECNICO_PARAMEDICO" in patient_prof[p][t][c]:
				patient_dic[p][t][4] += "_"  + "TM"*patient_prof[p][t][c].count("TECNICO_PARAMEDICO")

writer = open("log_estamentos_combinados.csv", "w")
writer.write(header)
for patient in patient_dic:
	for appointment in patient_dic[patient]:
		for ciap in patient_dic[patient][appointment][3]:
			writer.write(patient + ";" + patient_dic[patient][appointment][3][ciap][0] + ";" + patient_dic[patient][appointment][3][ciap][1] + ";" + patient_dic[patient][appointment][1] + ";" + patient_dic[patient][appointment][2] + ";" + ciap + ";" + patient_dic[patient][appointment][4] + "\n")
writer.close()

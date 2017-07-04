patient_cluster = {}

reader = open("cluster.csv", "r")
reader.readline()
for line in reader:
	lista = line.strip().split(";")
	patient = lista[0]
	cluster = lista[15]
	if patient not in patient_cluster:
		patient_cluster[patient] = cluster

reader.close()

reader = open("log_estamentos_combinados.csv", "r")
writer = open("log_estamentos_combinados_cluster.csv", "w")
writer.write(reader.readline().strip() + ";cluster\n")
for line in reader:
	patient = line.strip().split(";")[0]
	writer.write(line.strip() + ";" + patient_cluster[patient] + "\n")

reader.close()
writer.close()


from datetime import datetime, timedelta

def mean(lista):
    return sum(lista)/len(lista)

def delta(lista):
    x = 0
    for i in range(len(lista)-1):
        x += lista[i+1] - lista[i]
    return x/(len(lista)-1)

class Period:

    def __init__(self, transition, date, end):
        self.transition = transition
        self.start = date
        self.end = end

    def __repr__(self):
        return self.transition

reader = open("transition_log_V4.csv", "r")
measures = open("hba1c_3369.csv", "r")
writer = open("transition_measures.csv", "w")
writer.write("id_paciente;transicion;incio;fin;medicion_antes;medicion_ultima;variacion;delta_medio\n")
patient_measures = {}
patient_transitions = {}
measures.readline()
reader.readline()

for line in measures:
    lista = line.strip().split(';')
    patient = lista[0]
    time = lista[1]
    value = lista[2]
    if patient not in patient_measures:
        patient_measures[patient] = []
    patient_measures[patient].append([time, value])

for line in reader:
    lista = line.strip().split(';')
    patient = lista[0]
    transtion = lista[2]
    datestart = lista[3]
    dateend = lista[4]
    tup = (patient, datestart)
    if tup not in patient_transitions:
        patient_transitions[tup] = []
    patient_transitions[tup].append(Period(transtion, datestart, dateend))

for p in patient_transitions:
    t = patient_transitions[p]
    if len(t) > 1:
        pass
    else:
        measure_before = "nan"
        measure_between = []
        measure_last = "nan"
        for m in patient_measures[p[0]]:
            if datetime.strptime(m[0], "%d-%m-%y") <= datetime.strptime(t[0].start, "%d-%m-%y %H:%M"):
                measure_before = float(m[1])
            elif (datetime.strptime(m[0], "%d-%m-%y") - datetime.strptime(t[0].end, "%d-%m-%y %H:%M")).days < 90:
                measure_between.append(float(m[1]))
        if len(measure_between) > 0:
            measure_last = measure_between[-1]
        else:
            continue
        if measure_before != "nan":
            tendencia = ""
            estabilidad = ""
            sd = delta([measure_before] + measure_between)
            if measure_last - measure_before <= -0.5:
                tendencia = "mejora_mucho"
            elif 0.5 > measure_last - measure_before > - 0.5:
                if not (-0.1 < sd < 0.1):
                    if measure_last < measure_before:
                        tendencia = "mejora_poco"
                    else:
                        tendencia = "empeora_poco"
                else:
                    tendencia = "igual"
            else:
                tendencia = "empeora_mucho"

        else:
            measure_before = measure_between[0]
            sd = delta([measure_before] + measure_between)
            estabilidad = ""
            tendencia = ""
            if measure_last - measure_before <= -0.5:
                tendencia = "mejora_mucho"
            elif 0.5 > measure_last - measure_before > - 0.5:
                if not (-0.1 < sd < 0.1):
                    if measure_last < measure_before:
                        tendencia = "mejora_poco"
                    else:
                        tendencia = "empeora_poco"
                else:
                    tendencia = "igual"
            else:
                tendencia = "empeora_mucho"
        writer.write(p[0] + ";" + t[0].transition + ";" + t[0].start + ";" + t[0].end + ";" + str(measure_before) + ";" + str(measure_last) + ";" + tendencia + ";" + str(round(sd, 2)) + "\n")

print(patient_measures["89451"])

from datetime import datetime, timedelta

class Period:

    def __init__(self, patient):
        self.patient = patient
        self.current = 1
        self.previous = ""
        self.count_nodes = {}
        self.linear_pattern_nodes = []
        self.referral_pattern_nodes = []
        self.colaboration_pattern_nodes = []
        self.central_nodes = {}
        self.central_nodes["referral"] = []
        self.central_nodes["colaboration"] = []
        pass

class Node:

    def __init__(self, event, patient, start, end, estate, id, cluster, number_estate):
        self.event = event
        self.patient = patient
        self.start = start
        self.end = end
        self.estate = estate
        self.id = id
        self.cluster = cluster
        self.number_estate = number_estate
        self.type = ""
        self.type_number = 0
        self.referral_from = ""
        self.colaborate_with = ""

    def __repr__(self):
        return self.number_estate

class Pattern:

    def __init__(self, type, number):
        self.name = type
        self.number = number

###RESTRINGIR DERIVACIONES###
max_derivation_nodes = 5 ###nodos - 1
derivation_restricion = True
max_time_interval = 1.5
time_restriction = True
###RESTRINGIR DERIVACIONES###

file = "log_adherencia"
lineal_label = "Delegador"
lineal_auto_label = "Deleg. reasig."
derivation_label = "Der. Ciclica"
collaboration_label = "Contraderivacion"
hybrid_label = "Contraderivacion"
star_label = "Particip. Coord"
reader = open(file + ".csv", "r")
writer = open("report_" + file +"_V4.csv", "w")

###PARA CONTAR LOOPS DENTRO DE OTROS
contar_loop = False
###FIN CONTADOR DE LOOPS

reader.readline()
used_patients = []
used_periods = []
used_nodes = []
loop_stack = []

for line in reader:
    lista = line.strip().split(";")
    current_estate = lista[9]
    vino = lista[11] == "1"
    if datetime.strptime(lista[4], "%d-%m-%y %H:%M").year < 2012:
        continue
    if lista[6] not in ["MEDICO", "ENFERMERA", "NUTRICIONISTA"]:
        continue
    if lista[11] == "-1":
        continue
    current_node = Node(lista[0], lista[1], lista[4], lista[5], lista[6], lista[7], lista[8], lista[9])
    used_nodes.append(current_node)
    if lista[1] not in used_patients:
        derivation_count = 1
        colaboration_count = 1
        hybrid_count = 1
        loop_stack = []
        used_patients.append(lista[1])
        period = Period(lista[1])
        used_periods.append(period)
    else:
        period = used_periods[-1]
        current_node.referral_from = previous_node
    previous_node = current_node
    if current_node.number_estate not in period.count_nodes:
        period.count_nodes[current_node.number_estate] = 1
        period.previous = current_node
        loop_stack.append(current_node)
    else:
        if current_node.number_estate == period.previous.number_estate: #autoarco
            if period.previous.type != "":
                current_node.type = period.previous.type
                #current_node.type_number = period.previous.type_number
                current_node.type_number = period.previous.type.number
                if period.previous.colaborate_with != "":
                    current_node.colaborate_with = period.previous.colaborate_with
                loop_stack[-1] = current_node
            else:
                loop_stack.append(current_node)

            current_node.referral_from = period.previous.referral_from
            period.count_nodes[current_node.number_estate] += 1
            period.previous = current_node

        else: #hay que devolverse
            if current_node.number_estate == period.previous.colaborate_with:
                #current_node.type = period.previous.type
                #current_node.type_number = period.previous.type_number
                current_node.type = Pattern(period.previous.type.name, period.previous.type.number)
                current_node.type_number = current_node.type.number
                current_node.colaborate_with = period.previous.number_estate
                period.previous = current_node
                loop_stack[-1] = current_node
            elif not vino:
                effective_loop = False
            else:
                pattern_node_list = []
                node = loop_stack.pop()
                pattern_node_list.insert(0, node)
                effective_loop = True
                effective_colaboration = False
                while node.number_estate != current_node.number_estate:
                    if len(loop_stack) > 0:
                        if node.referral_from != "":
                            if node.referral_from.number_estate == current_estate and loop_stack[-1] == "loop" \
                                    and node.colaborate_with == current_estate:
                                effective_colaboration = True
                                break
                        node = loop_stack.pop()
                        if node == "break loop":
                            loop_stack.append("break loop")
                            for i in pattern_node_list:
                                loop_stack.append(i)
                            loop_stack.append(current_node)
                            effective_loop = False
                            break
                        if node != "loop":
                            pattern_node_list.insert(0, node)
                        else:
                            ##
                            if contar_loop:
                            ###
                                loop_count = 1
                                while node == "loop" and len(loop_stack) > 0 and node != "break loop":
                                    node = loop_stack.pop()
                                    loop_count += 1
                                if node == "loop" or node == "break loop":
                                    loop_stack.append("break loop")
                                    for i in pattern_node_list:
                                        loop_stack.append(i)
                                    loop_stack.append(current_node)
                                    effective_loop = False
                                    break
                                if node.number_estate != current_node.number_estate:
                                    pattern_node_list.insert(0, node)
                                elif node.number_estate == current_node.number_estate and len(pattern_node_list) > 1:
                                    pattern_node_list.insert(0, node)
                                else:
                                    loop_stack.append(node)
                                    loop_stack.append("break loop")
                                    for i in pattern_node_list:
                                        loop_stack.append(i)
                                    loop_stack.append(current_node)
                                    effective_loop = False
                                    break
                            ###
                            else:
                                loop_stack.append("break loop")
                                for i in pattern_node_list:
                                    loop_stack.append(i)
                                loop_stack.append(current_node)
                                effective_loop = False
                                break
                            ###z
                    else:
                        for i in pattern_node_list:
                            loop_stack.append(i)
                        loop_stack.append(current_node)
                        effective_loop = False
                        break
                if not effective_loop:
                    period.previous = current_node
                    continue
                if effective_colaboration:
                    if len(pattern_node_list) == 1:
                        pattern_node_list[-1].type.name = collaboration_label
                        pattern_node_list[-1].referral_from.type.name = collaboration_label
                        current_node.type.name = collaboration_label
                        current_node.type.number = colaboration_count
                        pattern_node_list[-1].type.number = colaboration_count
                        pattern_node_list[-1].referral_from.type.number = colaboration_count
                        current_node.type_number = colaboration_count
                        pattern_node_list[-1].type_number = colaboration_count
                        pattern_node_list[-1].referral_from.type_number = colaboration_count
                        current_node.colaborate_with = pattern_node_list[-1].number_estate
                        pattern_node_list[-1].referral_from.colaborate_with = pattern_node_list[-1].number_estate
                        pattern_node_list[-1].colaborate_with = current_node.number_estate
                        colaboration_count += 1
                        period.current += 1
                        period.previous = current_node
                        ##
                        if contar_loop:
                        ##
                            loop_stack.append("loop")
                            loop_stack.append(current_node)
                        ##
                        else:
                            loop_stack = ["loop", current_node]
                        ##
                    else:
                        loop_lenght = len(pattern_node_list)
                        if derivation_restricion and time_restriction:
                            start = datetime.strptime(pattern_node_list[0].start, "%d-%m-%y %H:%M")
                            finish = datetime.strptime(current_node.start, "%d-%m-%y %H:%M")
                            if loop_lenght <= max_derivation_nodes + 1 and (finish-start).days/365 <= max_time_interval:
                                for i in pattern_node_list:
                                    if i.type != "":
                                        i.type.name = hybrid_label
                                        i.type.number = hybrid_count
                                    else:
                                        i.type = Pattern(hybrid_label, hybrid_count)
                                if pattern_node_list[0].referral_from.type != "":
                                    pattern_node_list[0].referral_from.type.name = hybrid_label
                                    pattern_node_list[0].referral_from.type.number = hybrid_count
                                else:
                                    pattern_node_list[0].referral_from.type = Pattern(hybrid_label, hybrid_count)
                                    #pattern_node_list[0].referral_from.type.number = hybrid_count
                                current_node.type = Pattern(hybrid_label, hybrid_count)
                                #current_node.type_number = hybrid_count
                                hybrid_count += 1
                        elif derivation_restricion:
                            if loop_lenght <= max_derivation_nodes + 1:
                                for i in pattern_node_list:
                                    if i.type != "":
                                        i.type.name = hybrid_label
                                        i.type.number = hybrid_count
                                    else:
                                        i.type = Pattern(hybrid_label, hybrid_count)
                                if pattern_node_list[0].referral_from.type != "":
                                    pattern_node_list[0].referral_from.type.name = hybrid_label
                                    pattern_node_list[0].referral_from.type.number = hybrid_count
                                else:
                                    pattern_node_list[0].referral_from.type = Pattern(hybrid_label, hybrid_count)
                                current_node.type = Pattern(hybrid_label, hybrid_count)
                                hybrid_count += 1
                        elif time_restriction:
                            start = datetime.strptime(pattern_node_list[0].start, "%d-%m-%y %H:%M")
                            finish = datetime.strptime(current_node.start, "%d-%m-%y %H:%M")
                            if (finish-start).days/365 <= max_time_interval:
                                for i in pattern_node_list:
                                    if i.type != "":
                                        i.type.name = hybrid_label
                                        i.type.number = hybrid_count
                                    else:
                                        i.type = Pattern(hybrid_label, hybrid_count)
                                if pattern_node_list[0].referral_from.type != "":
                                    pattern_node_list[0].referral_from.type.name = hybrid_label
                                    pattern_node_list[0].referral_from.type.number = hybrid_count
                                else:
                                    pattern_node_list[0].referral_from.type = Pattern(hybrid_label, hybrid_count)
                                current_node.type = Pattern(hybrid_label, hybrid_count)
                                hybrid_count += 1
                        else:
                            for i in pattern_node_list:
                                if i.type != "":
                                    i.type.name = hybrid_label
                                    i.type.number = hybrid_count
                                else:
                                    i.type = Pattern(hybrid_label, hybrid_count)
                            if pattern_node_list[0].referral_from.type != "":
                                pattern_node_list[0].referral_from.type.name = hybrid_label
                                pattern_node_list[0].referral_from.type.number = hybrid_count
                            else:
                                pattern_node_list[0].referral_from.type = Pattern(hybrid_label, hybrid_count)
                                #pattern_node_list[0].referral_from.type.number = hybrid_count
                            current_node.type = Pattern(hybrid_label, hybrid_count)
                            #current_node.type_number = hybrid_count
                            hybrid_count += 1

                        period.current += 1
                        period.previous = current_node
                        ##
                        if contar_loop:
                        ##
                            loop_stack.append("loop")
                            loop_stack.append(current_node)
                        ##
                        else:
                            loop_stack = ["loop", current_node]
                        ##
                    continue


                pattern_node_list.append(current_node)
                loop_lenght = len(pattern_node_list) #si es colaboracion (loop de largo 3 nodos (M-N-M)) o derivacion (loop de largo > 3)
                if loop_lenght == 3:
                    pattern_node_list[0].colaborate_with = pattern_node_list[1].number_estate
                    pattern_node_list[1].colaborate_with = pattern_node_list[0].number_estate
                    pattern_node_list[2].colaborate_with = pattern_node_list[1].number_estate
                    for nodo in pattern_node_list:
                        nodo.type = Pattern(collaboration_label, colaboration_count)
                        #nodo.type_number = colaboration_count
                    pattern_node_list[0].type = pattern_node_list[2].type
                    colaboration_count += 1
                else:
                    if derivation_restricion and time_restriction:
                        start = datetime.strptime(pattern_node_list[0].start, "%d-%m-%y %H:%M")
                        finish = datetime.strptime(pattern_node_list[-1].start, "%d-%m-%y %H:%M")
                        if loop_lenght <= max_derivation_nodes and (finish-start).days/365 <= max_time_interval:
                            for nodo in pattern_node_list:
                                nodo.type = Pattern(derivation_label, derivation_count)
                                #nodo.type_number = derivation_count
                            derivation_count += 1
                        else:
                            pass
                    elif derivation_restricion:
                        if loop_lenght <= max_derivation_nodes:
                            for nodo in pattern_node_list:
                                nodo.type = Pattern(derivation_label, derivation_count)
                                #nodo.type_number = derivation_count
                            derivation_count += 1
                        else:
                            pass

                    elif time_restriction:
                        start = datetime.strptime(pattern_node_list[0].start, "%d-%m-%y %H:%M")
                        finish = datetime.strptime(pattern_node_list[-1].start, "%d-%m-%y %H:%M")
                        if (finish-start).days/365 <= max_time_interval:
                            for nodo in pattern_node_list:
                                nodo.type = Pattern(derivation_label, derivation_count)
                            derivation_count += 1
                    else:
                        for nodo in pattern_node_list:
                            nodo.type = Pattern(derivation_label, derivation_count)
                        derivation_count += 1
                period.current += 1
                period.previous = current_node
                ##
                if contar_loop:
                ##
                    loop_stack.append("loop")
                    loop_stack.append(current_node)
                ##
                else:
                    loop_stack = ["loop", current_node]
                ##

last_patient = ""
lineal_node_list = []
for nodo in used_nodes:
    if last_patient != nodo.patient:
        last_patient = nodo.patient
        if len(lineal_node_list) > 3:
            autorref = False
            for i in range(len(lineal_node_list)-1):
                if lineal_node_list[i].number_estate == lineal_node_list[i+1].number_estate:
                    autorref = True
                    break
            for i in lineal_node_list:
                if autorref:
                    i.type = Pattern(lineal_auto_label, 0)
                else:
                    i.type = Pattern(lineal_label, 0)
        lineal_node_list = []
    if nodo.type == "":
        lineal_node_list.append(nodo)
    else:
        if len(lineal_node_list) > 3:
            autorref = False
            for i in range(len(lineal_node_list)-1):
                if lineal_node_list[i].number_estate == lineal_node_list[i+1].number_estate:
                    autorref = True
                    break
            for i in lineal_node_list:
                if autorref:
                    i.type = Pattern(lineal_auto_label, 0)
                else:
                    i.type = Pattern(lineal_label, 0)
        lineal_node_list = []

if len(lineal_node_list) > 3:
    autorref = False
    for i in range(len(lineal_node_list)-1):
        if lineal_node_list[i].number_estate == lineal_node_list[i+1].number_estate:
            autorref = True
            break
    for i in lineal_node_list:
        if autorref:
            i.type = Pattern(lineal_auto_label, 0)
        else:
            i.type = Pattern(lineal_label, 0)

reader.close()

patient_patterns = {}
estate_starters = {}
nodo_anterior = ""
for nodo in used_nodes:
    first_time = False
    patient = nodo.patient
    if nodo.type!= "":
        treatment = str(nodo.type.name) + str(nodo.type.number)
    else:
        continue

    if patient not in patient_patterns:
        patient_patterns[patient] = {}
    if patient not in estate_starters:
        estate_starters[patient] = {}
    estate_dic = estate_starters[patient]
    if treatment not in patient_patterns[patient]:
        patient_patterns[patient][treatment] = []
        first_time = True
    if (first_time or nodo.colaborate_with == nodo_anterior):
        if nodo.number_estate not in estate_dic:
            estate_dic[nodo.number_estate] = []
        if treatment not in estate_dic[nodo.number_estate]:
            estate_dic[nodo.number_estate].append(treatment)
    patient_patterns[patient][treatment].append(nodo)
    if nodo_anterior != nodo.number_estate:
        nodo_anterior = nodo.number_estate

for p in patient_patterns:
    for estate in estate_starters[p]:
        if len(estate_starters[p][estate]) > 1 and "0" not in estate_starters[p][estate]:
            for pattern in estate_starters[p][estate]:
                for n in patient_patterns[p][pattern]:
                    n.type.name = star_label
                    n.type.number = "1"


writer.write("evento;id_paciente;fecha_inicio;fecha_fin;medico_estamento;medico_id;cluster;numero_estamento;segmento;id_segmento\n")
i = 1
for nodo in used_nodes:
    if nodo.type == "":
        nodo.type = Pattern("sin_tipo", 0)
    writer.write(str(i) + ';' + nodo.patient + ';' + nodo.start + ';' + nodo.end + ';' + nodo.estate + ';'
                 + nodo.id + ';' + nodo.cluster + ';' + nodo.number_estate + ';' + nodo.type.name + ';' + str(nodo.type.number) + '\n')
    i+= 1

writer.close()


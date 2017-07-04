import numpy as np
import operator
from graphviz import *
import math

times = 0

color_scale = ["#BBBBFF", "#AAAAFF", "#9999FF", "#8888FF", "#7777FF", "#6666FF", "#4444FF", "#2222FF", "#1111FF", "#0000FF"]
edge_scale = ["#F00000", "#F00000", "#F02800", "#F06800", "#F0A800", "#F2F000", "#81E400", "#35E400", "#08E400", "#08E400"]


def show_implicit_derivation(cluster, relations, activity_freq, act_derivations, patients_count, threshold, time,
                             arrow_threshold, freq_threshold, total_threshold, less_info=False, most_freq_filter=False):
    global times
    global color_scale
    if times == 0:
        bg = "#227722"
    else:
        bg = "#222277"

    text = 'digraph "Interacciones" { rankdir=TB;\nconcentrate = true;\nbgcolor = "' + bg + \
           '";\nfontcolor = "white";\nlabel = "Implicit Derivation (' + cluster + \
           '): \nrelation threshold = ' + str(threshold) + '   time = ' + str(time) + \
           '   derivation threshold = ' + str(arrow_threshold) + '   node freq = ' + str(freq_threshold) + \
           '   relation freq = ' + str(total_threshold) + '";\nlabelloc = "t";\n'
    totals = 0
    referrals = 0

    copy = dict(activity_freq)

    # list with activities that are not triggers
    invalid_triggers = []
    event_reader = open('Input/No_Triggers.txt', 'r')
    for line in event_reader:
        s = line.strip()
        invalid_triggers.append(s)

    # list with activities that are not considered when calculating the total of relations
    ignored_activities = []
    activity_reader = open('Input/No_Suma_Act.txt', 'r')
    for line in activity_reader:
        s = line.strip()
        ignored_activities.append(s)

    # Write report:
    raux = sorted(copy.items(), key=operator.itemgetter(1))
    daux = sorted(relations.items(), key=operator.itemgetter(1))


    file = 'Reports/Activity_frequency' + str(times) + '.txt'
    writer = open(file, 'w')
    for i in raux:
        if activity_freq[str(i[0])] < freq_threshold:
            del copy[str(i[0])]
            if less_info:
                continue
        writer.write(str(i[0]) + ':' + str(i[1]) + '\n')
    writer.write('\n\nSum: ' + str(np.sum(list(copy.values())))+'\nMean: ' + str(round(np.mean(list(copy.values())),3)) + '\nSD: ' + str(round(np.std(list(copy.values())),3)))
    writer.close()
    file = 'Reports/ID_Act_relation_frequency' + str(times) + '.txt'
    writer2= open(file, 'w')
    for i in daux:
        if activity_freq[str(i[0][0])] < freq_threshold or activity_freq[str(i[0][1])] < freq_threshold:
            del relations[(str(i[0][0]),str(i[0][1]))]
            if i[0][0] in act_derivations.keys():
                act_derivations[i[0][0]] -= i[1]
                if act_derivations[i[0][0]] == 0:
                    del act_derivations[i[0][0]]
                if less_info:
                    continue
        elif i[1] < total_threshold:
            del relations[(str(i[0][0]),str(i[0][1]))]
            if i[0][0] in act_derivations.keys():
                act_derivations[i[0][0]] -= i[1]
                if act_derivations[i[0][0]] == 0:
                    del act_derivations[i[0][0]]
                if less_info:
                    continue
        writer2.write(str(i[0][0]) + '->' + str(i[0][1]) + ':' + str(i[1]) + '\n')
    writer2.write('\n\nSum: ' + str(np.sum(list(relations.values())))+'\nMean: ' + str(round(np.mean(list(relations.values())),3)) + '\nSD: ' + str(round(np.std(list(relations.values())),3)) + '\nCases: ' + str(patients_count))
    writer2.close()

    dvaux = sorted(act_derivations.items(), key=operator.itemgetter(1))

    file = 'Reports/ID_Act_derivation_frequency' + str(times) + '.txt'
    writer3= open(file, 'w')
    for i in dvaux:
        if less_info:
            if activity_freq[str(i[0])] < freq_threshold:
                continue
        writer3.write(str(i[0]) + ':' + str(i[1]) + '\n')
    writer3.write('\n\nSum: ' + str(np.sum(list(act_derivations.values())))+'\nMean: ' + str(round(np.mean(list(act_derivations.values())),3)) + '\nSD: ' + str(round(np.std(list(act_derivations.values())),3)))
    writer3.close()

    for k in relations.keys():
        if k[0] in ignored_activities and k[1] in ignored_activities and most_freq_filter:
            continue
        totals += relations[k]
    for k in act_derivations.keys():
        referrals += act_derivations[k]

    print (totals, referrals)
    ###ACA EMPIEZA EL MANEJO DE LA PARTE GRAFICA EN SI###

    ###DIBUJO DE NODOS###
    for i in copy.keys():
        s = str(i).replace('-','')
        s = s.replace(' ','_')
        s = s.replace('_(C)','')
        s = s.replace('[S]_','')
        s = s.replace('+','_mas_')
        if(str(i) != 'nan'):
            shape = "hexagon"
            if(i not in invalid_triggers):
                if i in act_derivations.keys():
                    if(float(act_derivations[i])/referrals > arrow_threshold):
                        shape = "ellipse"

            text = text + s + ' [label =' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "'+ color_scale[int(activity_freq[i]*10/np.sum(list(activity_freq.values())))] +'" fontcolor = "black"]\n'
    ###DIBUJO DE ARCOS###
    for j in relations.keys():
        if (relations[j] < total_threshold):
            continue
        if j[0] in ignored_activities and j[1] in ignored_activities and most_freq_filter:
            del relations[j]
            continue
        if(activity_freq[str(j[0])] < freq_threshold or activity_freq[str(j[1])] < freq_threshold):
            continue
        x = float(relations[j])/totals
        x = round(x,3)
        if (x >= threshold):
            width = '  ' + str(x)
            stroke = str(8 * math.log(1 + x,2))
            arrow = str(2*(1/(2-x)))

            s1 = str(j[0]).replace('-','')
            s2 = str(j[1]).replace('-','')

            s1 = s1.replace(' ','_')
            s2 = s2.replace(' ','_')

            s1 = s1.replace('_(C)','')
            s2 = s2.replace('_(C)','')

            s1 = s1.replace('[S]_','')
            s2 = s2.replace('[S]_','')

            s1 = s1.replace('+','_mas_')
            s2 = s2.replace('+','_mas_')

            text = text + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "white" label = "'+ width + '" fontcolor = "black" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'

    text = text + '}'
    graf = Source(text)
    ###ARCHIVO EN FORMATO NOMBRE_THRESHOLD_TIME_ARROWTHRESHOLD.PDF
    filename = 'Graph-Output/ImplicitDerivation/ID' + str(times)+'_'+str(threshold)+'_'+str(time)+'_'+str(arrow_threshold)+str(freq_threshold)+'_'+str(total_threshold)
    times+=1
    #print texto
    graf.render(filename, view=True)

    return copy, relations


def show_implicit_derivation_role(cluster, dic, lista, res_derivations, estamentos, pacientes, threshold, time,
                                  arrow_threshold, freq_threshold, total_threshold, less_info=False):
    global times
    global color_scale
    if times == 0:
        bg = "#227722"
    else:
        bg = "#222277"
    text = 'digraph "Interacciones" { rankdir=TB;\nconcentrate = true;\nbgcolor = "' + bg + \
           '";\nfontcolor = "white";\nlabel = "Implicit Derivation (' + cluster + '): \nrelation threshold = ' + \
           str(threshold) + '   time = ' + str(time) + '   derivation threshold = ' + str(arrow_threshold) + \
           '   node freq = ' + str(freq_threshold) + '   relation freq = ' + str(total_threshold) +\
           '";\nlabelloc = "t";\n'
    #print texto
    totales = 0
    referrals = 0

    copia = dict(lista)

    raux = sorted(copia.items(), key=operator.itemgetter(1))
    daux = sorted(dic.items(), key=operator.itemgetter(1))

    file = 'Reports/Resource_frequency' + str(times) + '.txt'
    writer = open(file, 'w')
    for i in raux:
        if lista[str(i[0])] < freq_threshold:
            del copia[str(i[0])]
            if less_info:
                continue
        writer.write(str(i[0]) + ':' + str(i[1]) + '\n')
    writer.write('\n\nSum: ' + str(np.sum(list(copia.values())))+'\nMean: ' + str(round(np.mean(list(copia.values())),3)) + '\nSD: ' + str(round(np.std(list(copia.values())),3)))
    writer.close()

    file = 'Reports/ID_Res_relation_frequency'+str(times)+'.txt'
    writer2= open(file, 'w')
    for i in daux:
        if lista[str(i[0][0])] < freq_threshold or lista[str(i[0][1])] < freq_threshold:
            del dic[(str(i[0][0]),str(i[0][1]))]
            if i[0][0] in res_derivations.keys():
                res_derivations[i[0][0]] -= i[1]
                if res_derivations[i[0][0]] == 0:
                    del res_derivations[i[0][0]]
                if less_info:
                    continue
        elif i[1] < total_threshold:
            del dic[(str(i[0][0]),str(i[0][1]))]
            if i[0][0] in res_derivations.keys():
                res_derivations[i[0][0]] -= i[1]
                if res_derivations[i[0][0]] == 0:
                    del res_derivations[i[0][0]]
                if less_info:
                    continue
        writer2.write(str(i[0][0]) + '->' + str(i[0][1]) + ':' + str(i[1]) + '\n')
    writer2.write('\n\nSum: ' + str(np.sum(list(dic.values())))+'\nMean: ' + str(round(np.mean(list(dic.values())),3)) + '\nSD: ' + str(round(np.std(list(dic.values())),3)) + '\nCases: ' + str(pacientes))
    writer2.close()

    dvaux = sorted(res_derivations.items(), key=operator.itemgetter(1))

    file = 'Reports/ID_Res_derivation_frequency'+str(times)+'.txt'
    writer3= open(file, 'w')
    for i in dvaux:
        if less_info:
            if lista[str(i[0])] < freq_threshold:
                continue
        writer3.write(str(i[0]) + ':' + str(i[1]) + '\n')
    writer3.write('\n\nSum: ' + str(np.sum(list(res_derivations.values())))+'\nMean: ' + str(round(np.mean(list(res_derivations.values())),3)) + '\nSD: ' + str(round(np.std(list(res_derivations.values())),3)))
    writer3.close()

    for k in dic.keys():
        #if dic[k] >= total_threshold and lista[k[0]] >= freq_threshold and lista[k[1]] >= freq_threshold :
        totales += dic[k]
    for k in res_derivations.keys():
        #if res_derivations[k] >= mean + sd and lista[k] >= freq_threshold:
        referrals += res_derivations[k]

    print (totales, referrals)

    for i in copia.keys():

        s = str(i).replace('-','SIM')
        s = s.replace(' ','_')
        s = s.replace('_(C)','')
        s = s.replace('[S]_','')
        s = s.replace('+','_mas_')
        s = s.replace('(A)','A')
        s = s.replace('/A','')
        font = "black"
        shape = "none"
        fontname = "Times-Roman"
        if i in estamentos['MEDICO'] or s == 'MEDICO':
            shape = "hexagon"
        elif i in estamentos['ENFERMERA'] or s == 'ENFERMERA':
            shape = "box"
        #elif i in estamentos['MATRON(A)'] or s == 'MATRONA':
        #    shape = "circle"
        #elif i in estamentos['KINESIOLOGO'] or s == 'KINESIOLOGO':
        #    shape = "octagon"
        elif i in estamentos['NUTRICIONISTA'] or s == 'NUTRICIONISTA':
            shape = "ellipse"
        elif i in estamentos['TECNICO PARAMEDICO'] or s == 'TECNICO PARAMEDICO':
            shape = "doublecircle"
        #elif i in estamentos['ASISTENTE SOCIAL'] or s == 'ASISTENTE_SOCIAL':
        #    shape = "house"
        elif i in estamentos['ODONTOLOGO'] or s == 'ODONTOLOGO':
            shape = "trapezium"
        #elif i in estamentos['PSICOLOGO/A'] or s == 'PSICOLOGO':
        #    shape = "diamond"
        elif i in estamentos['TECNICO PARAMEDICO'] or s == 'TECNICO PARAMEDICO':
            shape = "triangle"
        #else:
        #    shape = "triangle"
        #    s = 'SIM'
        if(i in res_derivations.keys()):
            if(float(res_derivations[i])/referrals > arrow_threshold  and s != 'SIM'):
                font = "yellow"
                fontname = "Symbol"
        text = text + s + ' [label =' + s +  ' shape = ' + shape + ' style = "filled" fontname = "'+ fontname + '" fillcolor = "'+ color_scale[int(lista[i]*10/np.sum(list(lista.values())))] +'" fontcolor = "' + font + '"]\n'

    for j in dic.keys():
        if (dic[j] < total_threshold):
            continue
        if(lista[str(j[0])] < freq_threshold or lista[str(j[1])] < freq_threshold):
            continue

        x = float(dic[j])/totales
        x = round(x,3)
        if (x >= threshold):
            width = '  ' + str(x)
            stroke = str(8 * math.log(1 + x,2))
            arrow = str(2*(1/(2-x)))


            s1 = str(j[0]).replace('-','')
            s2 = str(j[1]).replace('-','')

            s1 = s1.replace(' ','_')
            s2 = s2.replace(' ','_')

            s1 = s1.replace('_(C)','')
            s2 = s2.replace('_(C)','')

            s1 = s1.replace('[S]_','')
            s2 = s2.replace('[S]_','')

            s1 = s1.replace('+','_mas_')
            s2 = s2.replace('+','_mas_')

            s1 = s1.replace('(A)','A')
            s2 = s2.replace('(A)','A')

            s1 = s1.replace('/A','')
            s2 = s2.replace('/A','')

            text = text + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "black" label = "'+ width + '" fontsize = "30" fontcolor = "black" fontsize = "8" style = "solid" penwidth = '+ stroke + ']\n'
        #else:
            #del dic[j]
            #continue
    text = text + '}'
    graf = Source(text)
    ###ARCHIVO EN FORMATO NOMBRE_THRESHOLD_TIME_ARROWTHRESHOLD.PDF

    filename = 'Graph-Output/ImplicitDerivation/ID' + str(times)+'_'+str(threshold)+'_'+str(time)+'_'+str(arrow_threshold)+'_'+str(freq_threshold)+'_'+str(total_threshold)
    times += 1
    graf.render(filename, view=True)

    return (copia, dic)

def showDuo(file, dic, lista, estamentos, threshold, freq_threshold, total_threshold, time):
    global times
    global color_scale

    if times == 0:
        bg = "#227722"
    else:
        bg = "#222277"

    texto = 'digraph "Interacciones" { rankdir=TB;\nconcentrate = true;\nnode [shape=box style = filled fillcolor = "#88FFFF"];\nbgcolor = "' + bg + '";\nfontcolor = "white";\nlabel = "Duo ('+ file + '): \nrelation threshold = ' + str(threshold) + '   time = ' + str(time) + '   node freq = ' + str(freq_threshold)+ '   relation freq = ' + str(total_threshold) +'";\nlabelloc = "t";\n'

    #texto = texto + 'node [shape=plaintext];\nsubgraph cluster_01 {\n'+ 'rankdir=LR label = "Legend";\nfontcolor = "white"\nkey [label=<<table border="0" cellpadding="2" cellspacing="0" cellborder="0">\n<tr><td align="right" port="i1">Dos profesionales</td></tr>\n<tr><td align="right" port="i2">Tres profesionales</td></tr>\n<tr><td align="right" port="i3">Cuatro profesionales</td></tr>\n</table>>]\nkey2 [label=<<table border="0" cellpadding="2" cellspacing="0" cellborder="0">\n<tr><td port="i1">&nbsp;</td></tr>\n<tr><td port="i2">&nbsp;</td></tr>\n<tr><td port="i3">&nbsp;</td></tr>\n</table>>]\nkey:i1:e -> key2:i1:w [color=white]\nkey:i2:e -> key2:i2:w [color=orange head = "none"]\nkey:i3:e -> key2:i3:w [color=red head = "none"]\n} \n'


    totales = 0
    for k in dic.keys():
        totales += dic[k]

    for i in lista.keys():

        s = str(i).replace('-','')
        s = s.replace(' ','_')
        s = s.replace('_(C)','')
        s = s.replace('[S]_','')
        s = s.replace('+','_mas_')
        s = s.replace('(A)','A')
        s = s.replace('/A','')
        font = "white"
        shape = "box"
        if i in estamentos['MEDICO'] or s == 'MEDICO' or s == 'MEDICO_' or s == 'MEDICO__':
            shape = "hexagon"
        elif i in estamentos['ENFERMERA'] or s == 'ENFERMERA' or s == 'ENFERMERA_' or s == 'ENFERMERA__':
            shape = "box"
        elif i in estamentos['MATRON(A)'] or s == 'MATRONA':
            shape = "circle"
        elif i in estamentos['KINESIOLOGO'] or s == 'KINESIOLOGO':
            shape = "octagon"
        elif i in estamentos['NUTRICIONISTA'] or s == 'NUTRICIONISTA':
            shape = "ellipse"
        elif i in estamentos['TECNICO PARAMEDICO'] or s == 'TECNICO PARAMEDICO':
            shape = "doublecircle"
        elif i in estamentos['ASISTENTE SOCIAL'] or s == 'ASISTENTE_SOCIAL' or s == 'ASISTENTE_SOCIAL_' or s == 'ASISTENTE_SOCIAL__':
            shape = "house"
        elif i in estamentos['ODONTOLOGO'] or s == 'ODONTOLOGO':
            shape = "trapezium"
        elif i in estamentos['PSICOLOGO/A'] or s == 'PSICOLOGO' or s == 'PSICOLOGO_' or s == 'PSICOLOGO__':
            shape = "diamond"
        elif i in estamentos['ADMINISTRADOR'] or i in estamentos['ADMINISTRATIVO'] or s == 'ADMINISTRADOR' or s == 'ADMINISTRATIVO' or s == 'SALA DE PROCEDIMIENTOS':
            shape = "triangle"

        texto = texto + s + ' [label =' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "'+ color_scale[int(lista[i]*10/np.sum(list(lista.values())))] +'" fontcolor = ' + font + ']\n'

    for j in dic.keys():
        if (dic[j] < total_threshold):
            continue
        if len(j) == 2:
            if(lista[str(j[0])] < freq_threshold or lista[str(j[1])] < freq_threshold):
                continue
        elif len(j) == 3:
            if(lista[j[0][:len(j[0])-1]] < freq_threshold or lista[j[1][:len(j[1])-1]] < freq_threshold or lista[j[2][:len(j[2])-1]] < freq_threshold):
                continue
        elif len(j) == 4:
            if(lista[j[0][:len(j[0])-2]] < freq_threshold or lista[j[1][:len(j[1])-2]] < freq_threshold or lista[j[2][:len(j[2])-2]] < freq_threshold or lista[j[3][:len(j[3])-2]] < freq_threshold):
                continue

        x = float(dic[j])/totales
        x = round(x,3)
        if (x >= threshold):
            width = ' ' + str(x)
            stroke = str(8 * math.log(1 + x,2))
            arrow = str(2*(1/(2-x)))

            s1 = str(j[0]).replace('-','')
            s2 = str(j[1]).replace('-','')

            s1 = s1.replace(' ','_')
            s2 = s2.replace(' ','_')

            s1 = s1.replace('_(C)','')
            s2 = s2.replace('_(C)','')

            s1 = s1.replace('[S]_','')
            s2 = s2.replace('[S]_','')

            s1 = s1.replace('+','_mas_')
            s2 = s2.replace('+','_mas_')

            s1 = s1.replace('(A)','A')
            s2 = s2.replace('(A)','A')

            s1 = s1.replace('/A','')
            s2 = s2.replace('/A','')

            if len(j) > 2:
                s3 = str(j[2]).replace('-','')
                s3 = s3.replace(' ','_')
                s3 = s3.replace('_(C)','')
                s3 = s3.replace('[S]_','')
                s3 = s3.replace('+','_mas_')
                s3 = s3.replace('(A)','A')
                s3 = s3.replace('/A','')
                if len(j) > 3:
                    s4 = str(j[3]).replace('-','')
                    s4 = s4.replace(' ','_')
                    s4 = s4.replace('_(C)','')
                    s4 = s4.replace('[S]_','')
                    s4 = s4.replace('+','_mas_')
                    s4 = s4.replace('(A)','A')
                    s4 = s4.replace('/A','')

                    if s1 == s2 == s3 == s4:
                        s1 = s1 + 'A'
                        s2 = s2 + 'B'
                        s3 = s3 + 'C'
                        s4 = s4 + 'D'
                    elif s1 == s2 == s3:
                        s1 = s1 + 'A'
                        s2 = s2 + 'B'
                        s3 = s3 + 'C'
                        s4 = s4[:len(s4)-1]
                    elif s1 == s2 == s4:
                        s1 = s1 + 'A'
                        s2 = s2 + 'B'
                        s4 = s4 + 'C'
                        s3 = s3[:len(s3)-1]
                    elif s1 == s3 == s4:
                        s1 = s1 + 'A'
                        s3 = s3 + 'B'
                        s4 = s4 + 'C'
                        s2 = s2[:len(s2)-1]
                    elif s2 == s3 == s4:
                        s2 = s2 + 'A'
                        s3 = s3 + 'B'
                        s4 = s4 + 'C'
                        s1 = s1[:len(s1)-1]

                    elif s1 == s2 and s3 == s4:
                        s1 = s1 + 'A'
                        s2 = s2 + 'B'
                        s3 = s3 + 'A'
                        s4 = s4 + 'B'

                    elif s1 == s3 and s2 == s4:
                        s1 = s1 + 'A'
                        s3 = s3 + 'B'
                        s2 = s2 + 'A'
                        s4 = s4 + 'B'

                    elif s1 == s4 and s2 == s3:
                        s1 = s1 + 'A'
                        s4 = s4 + 'B'
                        s2 = s2 + 'A'
                        s3 = s3 + 'B'

                    elif s1 == s2:
                        s1 = s1 + 'A'
                        s2 = s2 + 'B'
                        s3 = s3[:len(s3)-1]
                        s4 = s4[:len(s4)-1]
                    elif s1 == s3:
                        s1 = s1 + 'A'
                        s3 = s3 + 'B'
                        s2 = s2[:len(s2)-1]
                        s4 = s4[:len(s4)-1]
                    elif s1 == s4:
                        s1 = s1 + 'A'
                        s4 = s4 + 'B'
                        s3 = s3[:len(s3)-1]
                        s2 = s2[:len(s2)-1]
                    elif s2 == s3:
                        s2 = s2 + 'A'
                        s3 = s3 + 'B'
                        s1 = s1[:len(s1)-1]
                        s4 = s4[:len(s4)-1]
                    elif s2 == s4:
                        s2 = s2 + 'A'
                        s4 = s4 + 'B'
                        s3 = s3[:len(s3)-1]
                        s1 = s1[:len(s1)-1]
                    elif s3 == s4:
                        s3 = s3 + 'A'
                        s4 = s4 + 'B'
                        s1 = s1[:len(s1)-1]
                        s2 = s2[:len(s2)-1]
                    else:
                        s1 = s1[:len(s1)-1]
                        s2 = s2[:len(s2)-1]
                        s3 = s3[:len(s3)-1]
                        s4 = s4[:len(s4)-1]

                    texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "red" dir = "none" label = "'+ width + '" fontcolor = "yellow" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'
                    texto = texto + s4 + '->' + s1 + '[arrowsize = '+ arrow + ' color = "red" dir = "none" fontcolor = "yellow" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'
                    texto = texto + s2 + '->' + s3 + '[arrowsize = '+ arrow + ' color = "red" dir = "none" fontcolor = "yellow" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'
                    texto = texto + s3 + '->' + s4 + '[arrowsize = '+ arrow + ' color = "red" dir = "none" fontcolor = "yellow" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'

                else:
                    if s1 == s2 == s3:
                        s1 = s1 + 'A'
                        s2 = s2 + 'B'
                        s3 = s3 + 'C'

                    elif s1 == s2:
                        s1 = s1 + 'A'
                        s2 = s2 + 'B'
                        s3 = s3[:len(s3)-1]

                    elif s3 == s2:
                        s2 = s2 + 'A'
                        s3 = s3 + 'B'
                        s1 = s1[:len(s1)-1]

                    elif s1 == s3:
                        s1 = s1 + 'A'
                        s3 = s3 + 'B'
                        s2 = s2[:len(s2)-1]

                    else:
                        s1 = s1[:len(s1)-1]
                        s2 = s2[:len(s2)-1]
                        s3 = s3[:len(s3)-1]

                    texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "orange" dir = "none" label = "'+ width + '" fontcolor = "yellow" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'
                    texto = texto + s3 + '->' + s1 + '[arrowsize = '+ arrow + ' color = "orange" dir = "none" fontcolor = "yellow" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'
                    texto = texto + s2 + '->' + s3 + '[arrowsize = '+ arrow + ' color = "orange" dir = "none" fontcolor = "yellow" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'

            else:
                texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "white" dir = "none" label = "'+ width + '" fontcolor = "yellow" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'

    texto = texto + '}'
    graf = Source(texto)
    ###ARCHIVO EN FORMATO NOMBRE_THRESHOLD_TIME_ARROWTHRESHOLD.PDF
    filename = 'Graph-Output/Duo' + str(times)+'_'+str(threshold)+'_'+str(time)+'_'+str(freq_threshold)+'_'+str(total_threshold)
    times += 1
    graf.render(filename, view=True)

    return lista, dic

def showExplicitDerivation(cluster, referrals_estates, avg_annual_attentions, referrals_estates_withfail, referrals_estates_labeled, role_frequency, threshold, labeled_prof_threshold, freq_threshold, total_threshold, absolute_rel_threshold, time, patients):
    global times
    global color_scale

    if times == 0:
        bg = "#227722"
    else:
        bg = "#222277"

    bg_adherence = "#646464"

    texto = 'digraph "Interacciones" { rankdir=TB;\nbgcolor = "'+ bg_adherence + '";\nfontcolor = "white";\nlabel = "ED annual average relation per patient ('+ cluster + '). Derivations:' + str(np.sum(list(referrals_estates.values()))) + ' Sample: '+ str(patients) +'\nrelation threshold = ' + str(threshold) + '   time = ' + str(time) + '   node freq = ' + str(freq_threshold)+ '   relation freq = ' + str(total_threshold) +'";\nlabelloc = "t";\n'
    texto2 = 'digraph "Interacciones" { rankdir=TB;\nconcentrate = true;\nbgcolor = "'+ bg + '";\nfontcolor = "white";\nlabel = "ED relation frequency ('+ cluster + '). Derivations:' + str(np.sum(list(referrals_estates.values()))) + ' Sample: '+ str(patients) + '\nrelation threshold = ' + str(threshold) + '   time = ' + str(time) + '   node freq = ' + str(freq_threshold)+ '   relation freq = ' + str(absolute_rel_threshold) +'";\nlabelloc = "t";\n'
    texto3 = 'digraph "Interacciones" { rankdir=TB;\nconcentrate = true;\nbgcolor = "'+ bg_adherence + '";\nfontcolor = "white";\nlabel = "ED adherence ('+ cluster + '). Derivations:' + str(np.sum(list(referrals_estates.values()))) + ' Sample: '+ str(patients) + '\nrelation threshold = ' + str(threshold) + '   time = ' + str(time) + '   node freq = ' + str(freq_threshold)+ '   relation freq = ' + str(absolute_rel_threshold) +'";\nlabelloc = "t";\n'
    texto4 = 'digraph "Interacciones" { rankdir=TB;\nconcentrate = true;\nbgcolor = "'+ bg_adherence + '";\nfontcolor = "white";\nlabel = "ED labeled relation frequency ('+ cluster + '). Derivations:' + str(np.sum(list(referrals_estates.values()))) + ' Sample: '+ str(patients) + '\nrelation threshold = ' + str(threshold) + '   time = ' + str(time) + '   node freq = ' + str(freq_threshold)+ '   relation freq = ' + str(absolute_rel_threshold) +'";\nlabelloc = "t";\n'

    #texto = texto + 'node [shape=plaintext];\nsubgraph cluster_01 {\n'+ 'rankdir=LR label = "Legend";\nfontcolor = "white"\nkey [label=<<table border="0" cellpadding="2" cellspacing="0" cellborder="0">\n<tr><td align="right" port="i1">Efectivas</td></tr>\n<tr><td align="right" port="i2">No efectivas</td></tr>\n</table>>]\nkey2 [label=<<table border="0" cellpadding="2" cellspacing="0" cellborder="0">\n<tr><td port="i1">&nbsp;</td></tr>\n<tr><td port="i2">&nbsp;</td></tr>\n</table>>]\nkey:i1:e -> key2:i1:w [color=green]\nkey:i2:e -> key2:i2:w [color=orange head = "tee"]\n} \n'

    totales = 0

    success_rate = {}

    for k in referrals_estates_withfail.keys():
        if (referrals_estates_withfail[k] < total_threshold):
            continue
        if role_frequency[k[0]] < freq_threshold:
            continue
        if str(k[1]) != 'MED_FAIL' and str(k[1]) != 'ENF_FAIL' and str(k[1]) != 'NUT_FAIL':
            if role_frequency[k[1]] < freq_threshold:
                continue
        totales += referrals_estates_withfail[k]
        if k[1] == 'MED_FAIL':
            aux = 'MEDICO'
        elif k[1] == 'ENF_FAIL':
            aux = 'ENFERMERA'
        elif k[1] == 'NUT_FAIL':
            aux = 'NUTRICIONISTA'
        else:
            aux = k[1]

        tuple = (k[0], aux)
        if tuple not in success_rate.keys():
            success_rate[tuple] = 0
        success_rate[tuple] += referrals_estates_withfail[k]

    print (referrals_estates_withfail)
    print (success_rate)

    if ('MEDICO' in role_frequency and "ENFERMERA" in role_frequency and "NUTRICIONISTA" in role_frequency):
        texto = texto + "MEDICO" + ' [label =' + "MEDICO" +  ' shape = ' + "hexagon" + ' style = "filled" fillcolor = "'+ color_scale[int(role_frequency["MEDICO"]*10/np.sum(list(role_frequency.values())))] +'" fontcolor = ' + "black" + ']\n'
        texto = texto + "ENFERMERA" + ' [label =' + "ENFERMERA" +  ' shape = ' + "box" + ' style = "filled" fillcolor = "'+ color_scale[int(role_frequency["ENFERMERA"]*10/np.sum(list(role_frequency.values())))] +'" fontcolor = ' + "black" + ']\n'
        texto = texto + "NUTRICIONISTA" + ' [label =' + "NUTRICIONISTA" +  ' shape = ' + "ellipse" + ' style = "filled" fillcolor = "'+ color_scale[int(role_frequency["NUTRICIONISTA"]*10/np.sum(list(role_frequency.values())))] +'" fontcolor = ' + "black" + ']\n'
        texto2 = texto2 + "MEDICO" + ' [label =' + "MEDICO" +  ' shape = ' + "hexagon" + ' style = "filled" fillcolor = "'+ color_scale[int(role_frequency["MEDICO"]*10/np.sum(list(role_frequency.values())))] +'" fontcolor = ' + "black" + ']\n'
        texto2 = texto2 + "ENFERMERA" + ' [label =' + "ENFERMERA" +  ' shape = ' + "box" + ' style = "filled" fillcolor = "'+ color_scale[int(role_frequency["ENFERMERA"]*10/np.sum(list(role_frequency.values())))] +'" fontcolor = ' + "black" + ']\n'
        texto2 = texto2 + "NUTRICIONISTA" + ' [label =' + "NUTRICIONISTA" +  ' shape = ' + "ellipse" + ' style = "filled" fillcolor = "'+ color_scale[int(role_frequency["NUTRICIONISTA"]*10/np.sum(list(role_frequency.values())))] +'" fontcolor = ' + "black" + ']\n'
        texto3 = texto3 + "MEDICO" + ' [label =' + "MEDICO" +  ' shape = ' + "hexagon" + ' style = "filled" fillcolor = "'+ color_scale[int(role_frequency["MEDICO"]*10/np.sum(list(role_frequency.values())))] +'" fontcolor = ' + "black" + ']\n'
        texto3 = texto3 + "ENFERMERA" + ' [label =' + "ENFERMERA" +  ' shape = ' + "box" + ' style = "filled" fillcolor = "'+ color_scale[int(role_frequency["ENFERMERA"]*10/np.sum(list(role_frequency.values())))] +'" fontcolor = ' + "black" + ']\n'
        texto3 = texto3 + "NUTRICIONISTA" + ' [label =' + "NUTRICIONISTA" +  ' shape = ' + "ellipse" + ' style = "filled" fillcolor = "'+ color_scale[int(role_frequency["NUTRICIONISTA"]*10/np.sum(list(role_frequency.values())))] +'" fontcolor = ' + "black" + ']\n'
    else:
        for i in role_frequency.keys():
            s = str(i).replace('-','')
            s = s.replace(' ','_')
            s = s.replace('_(C)','')
            s = s.replace('[S]_','')
            s = s.replace('+','_mas_')
            s = s.replace('(A)','A')
            s = s.replace('/A','')
            font = "black"
            if s == 'MEDICO':
                shape = "hexagon"
            elif s == 'ENFERMERA':
                shape = "box"
            elif s == 'NUTRICIONISTA':
                shape = "ellipse"
            else:
                continue
            texto = texto + s + ' [label =' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "'+ color_scale[int(role_frequency[i]*10/np.sum(list(role_frequency.values())))] +'" fontcolor = ' + font + ']\n'
            texto2 = texto2 + s + ' [label =' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "'+ color_scale[int(role_frequency[i]*10/np.sum(list(role_frequency.values())))] +'" fontcolor = ' + font + ']\n'
            texto3 = texto3 + s + ' [label =' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "'+ color_scale[int(role_frequency[i]*10/np.sum(list(role_frequency.values())))] +'" fontcolor = ' + font + ']\n'

    for k in referrals_estates_labeled:
        for i in k:
            s = str(i).replace('-','')
            s = s.replace(' ','_')
            s = s.replace('_(C)','')
            s = s.replace('[S]_','')
            s = s.replace('+','_mas_')
            s = s.replace('(A)','A')
            s = s.replace('/A','')
            font = "black"
            role = ''
            if s.find('MEDICO') >= 0:
                shape = "hexagon"
                role = "MEDICO"
            elif s.find('ENFERMERA') >= 0:
                shape = "box"
                role = "ENFERMERA"
            elif s.find('NUTRICIONISTA') >= 0:
                shape = "ellipse"
                role = "NUTRICIONISTA"
            else:
                continue
            texto4 = texto4 + s + ' [label =' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "'+ color_scale[int(role_frequency[role]*10/np.sum(list(role_frequency.values())))] +'" fontcolor = ' + font + ']\n'

    for j in referrals_estates_withfail.keys():
        if (referrals_estates_withfail[j] < total_threshold):
            continue
        if str(j[1]) != 'MED_FAIL' and str(j[1]) != 'ENF_FAIL' and str(j[1]) != 'NUT_FAIL':
            if role_frequency[str(j[1])] < freq_threshold:
                continue
        if(role_frequency[str(j[0])] < freq_threshold):
            continue

        repetido = True

        if j[1] == 'MED_FAIL':
            aux = 'MEDICO'
        elif j[1] == 'ENF_FAIL':
            aux = 'ENFERMERA'
        elif j[1] == 'NUT_FAIL':
            aux = 'NUTRICIONISTA'
        else:
            aux = j[1]
            repetido = False

        tupla = (j[0], aux)
        ###x for adherence
        ###y for % of relations/total
        ###z for annual relations/#patients
        if success_rate[tupla] <= 0:
            continue
        x = float(referrals_estates_withfail[j])/success_rate[tupla]
        x = round(x,3)
        y = float(success_rate[tupla])/totales *100
        absolute_freq = success_rate[tupla]
        y = round(y, 3)

        if (x >= threshold):
            width = ' ' + str(round(x*100, 2)) + '%, ' + str(absolute_freq)
            stroke = str(2.8 * math.log(1.25 + x,2))
            arrow = str(1*(1/(2-x)))


            s1 = str(j[0]).replace('-','')
            s2 = str(j[1]).replace('-','')

            s1 = s1.replace(' ','_')
            s2 = s2.replace(' ','_')

            s1 = s1.replace('_(C)','')
            s2 = s2.replace('_(C)','')

            s1 = s1.replace('[S]_','')
            s2 = s2.replace('[S]_','')

            s1 = s1.replace('+','_mas_')
            s2 = s2.replace('+','_mas_')

            s1 = s1.replace('(A)','A')
            s2 = s2.replace('(A)','A')

            s1 = s1.replace('/A','')
            s2 = s2.replace('/A','')
            if (str(j[1]) != 'MED_FAIL' and str(j[1]) != 'ENF_FAIL' and str(j[1]) != 'NUT_FAIL'):
                head = 'normal'
                color_pos = int(x * 10)
                if color_pos > 9:
                    color_pos = 9
                color = edge_scale[color_pos]
            else:
                continue
                '''
                head = 'normal'
                color = 'orange'
                if str(j[1]) == 'MED_FAIL':
                    s2 = 'MEDICO'
                elif str(j[1]) == 'ENF_FAIL':
                    s2 = 'ENFERMERA'
                elif str(j[1]) == 'NUT_FAIL':
                    s2 = 'NUTRICIONISTA'
                '''
            texto3 = texto3 + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "' + color + '" label = "'+ width + '" arrowhead = ' + head + ' fontcolor = "white" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'


        if y >= threshold:
            if repetido:
                continue

            width = '  ' + str(y) + '%\n  '
            stroke = str(1 * math.log(1 + y,2))
            arrow = str(0.8 * math.log(1 + y,10))


            s1 = str(j[0]).replace('-','')
            s2 = str(j[1]).replace('-','')

            s1 = s1.replace(' ','_')
            s2 = s2.replace(' ','_')

            s1 = s1.replace('_(C)','')
            s2 = s2.replace('_(C)','')

            s1 = s1.replace('[S]_','')
            s2 = s2.replace('[S]_','')

            s1 = s1.replace('+','_mas_')
            s2 = s2.replace('+','_mas_')

            s1 = s1.replace('(A)','A')
            s2 = s2.replace('(A)','A')

            s1 = s1.replace('/A','')
            s2 = s2.replace('/A','')
            head = 'normal'

            texto2 = texto2 + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "white" label = "'+ width + '" arrowhead = ' + head + ' fontcolor = "black" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'

    for k in list(avg_annual_attentions.keys()):
        
        if len(avg_annual_attentions[k]) == 0:
            continue
        z = round(np.mean(list(avg_annual_attentions[k])), 3)
        if (z < absolute_rel_threshold):
            continue
        
        #width = '  ' + str(z) +  '\nsd: ' +str(round(np.std(list(avg_annual_attentions[k])),3))
        width = ' ' + str(z) +  '\n ' +str(round(len(avg_annual_attentions[k])/patients * 100, 2)) + ' %'
        
        stroke = str(3 * math.log(1 + z,2))
        arrow = "1.2"


        s1 = str(k[0]).replace('-','')
        s2 = str(k[1]).replace('-','')

        s1 = s1.replace(' ','_')
        s2 = s2.replace(' ','_')

        s1 = s1.replace('_(C)','')
        s2 = s2.replace('_(C)','')

        s1 = s1.replace('[S]_','')
        s2 = s2.replace('[S]_','')

        s1 = s1.replace('+','_mas_')
        s2 = s2.replace('+','_mas_')

        s1 = s1.replace('(A)','A')
        s2 = s2.replace('(A)','A')

        s1 = s1.replace('/A','')
        s2 = s2.replace('/A','')
        head = 'normal'

        texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "white" label = "'+ width + '" arrowhead = ' + head + ' fontcolor = "white" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'

    total_labeled_referrals = 0
    for k in referrals_estates_labeled:
        total_labeled_referrals += referrals_estates_labeled[k]

    for k in referrals_estates_labeled:
        x = float(referrals_estates_labeled[k])/total_labeled_referrals
        if x < labeled_prof_threshold:
            continue
        width = '  ' + str(x)
        stroke = str(3 * math.log(1 + x,2))
        arrow = str(1*(1/(3-x)))
        if float(arrow) < 0:
            arrow = "2"

        s1 = str(k[0]).replace('-','')
        s2 = str(k[1]).replace('-','')
        s1 = s1.replace(' ','_')
        s2 = s2.replace(' ','_')
        s1 = s1.replace('_(C)','')
        s2 = s2.replace('_(C)','')
        s1 = s1.replace('[S]_','')
        s2 = s2.replace('[S]_','')
        s1 = s1.replace('+','_mas_')
        s2 = s2.replace('+','_mas_')
        s1 = s1.replace('(A)','A')
        s2 = s2.replace('(A)','A')
        s1 = s1.replace('/A','')
        s2 = s2.replace('/A','')
        head = 'normal'
        texto4 = texto4 + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "white" label = "'+ width + '" arrowhead = ' + head + ' fontcolor = "yellow" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'

    texto = texto + '}'
    graf = Source(texto)
    ###ARCHIVO EN FORMATO NOMBRE_THRESHOLD_TIME_ARROWTHRESHOLD.PDF
    filename = 'Graph-Output/ExplicitDerivation/ED_Avg_Referrals' + str(times)+'_'+str(threshold)+'_'+str(time)+'_'+str(freq_threshold)+'_'+str(total_threshold)
    times += 1
    graf.render(filename, view=True)

    texto2 = texto2 + '}'
    graf = Source(texto2)
    ###ARCHIVO EN FORMATO NOMBRE_THRESHOLD_TIME_ARROWTHRESHOLD.PDF
    filename = 'Graph-Output/ExplicitDerivation/ED' + str(times)+'_'+str(threshold)+'_'+str(time)+'_'+str(freq_threshold)+'_'+str(total_threshold)
    times += 1
    graf.render(filename, view=True)

    texto3 = texto3 + '}'
    graf = Source(texto3)
    ###ARCHIVO EN FORMATO NOMBRE_THRESHOLD_TIME_ARROWTHRESHOLD.PDF
    filename = 'Graph-Output/ExplicitDerivation/Adherence ' + str(times)+'_'+str(threshold)+'_'+str(time)+'_'+str(freq_threshold)+'_'+str(total_threshold)
    times += 1
    graf.render(filename, view=True)

    texto4 = texto4 + '}'
    graf = Source(texto4)
    ###ARCHIVO EN FORMATO NOMBRE_THRESHOLD_TIME_ARROWTHRESHOLD.PDF
    filename = 'Graph-Output/ExplicitDerivation/ED_LABELED' + str(times)+'_'+str(threshold)+'_'+str(time)+'_'+str(freq_threshold)+'_'+str(total_threshold)
    times += 1
    graf.render(filename, view=True)


def showLogContrast(node1, relation1, node2, relation2, node_threshold,  relation_threshold, estamentos, differences, filter = True):

    texto = 'digraph "Contraste" { rankdir=TB;\nnode [shape=box style = filled fillcolor = "#88FFFF"];\nbgcolor = "#6C6C6C";\nfontcolor = "white";\nlabel = "Contrast: \nNode Significance = ' + str(node_threshold) + '   Relation Significance = ' + str(relation_threshold) + '";\nlabelloc = "t";\n'

    lista_malos = [] ###Nodos que no se toman en cuenta si aparecen en ambos logs pero la frecuencia es menor al threshold
    for i in node1.keys():
        s = str(i).replace('-','')
        s = s.replace(' ','_')
        s = s.replace('_(C)','')
        s = s.replace('[S]_','')
        s = s.replace('+','_mas_')
        s = s.replace('(A)','A')
        s = s.replace('/A','')
        font = "black"
        shape = "box"
        if i in estamentos['MEDICO'] or s in ['MEDICO', 'MED_FAIL']:
            shape = "hexagon"
        elif i in estamentos['ENFERMERA'] or s in ['ENFERMERA', 'ENF_FAIL']:
            shape = "box"
        elif i in estamentos['MATRON(A)'] or s == 'MATRONA':
            shape = "circle"
        elif i in estamentos['KINESIOLOGO'] or s == 'KINESIOLOGO':
            shape = "octagon"
        elif i in estamentos['NUTRICIONISTA'] or s in ['NUTRICIONISTA', 'NUT_FAIL']:
            shape = "ellipse"
        elif i in estamentos['TECNICO PARAMEDICO'] or s == 'TECNICO PARAMEDICO':
            shape = "doublecircle"
        elif i in estamentos['ASISTENTE SOCIAL'] or s == 'ASISTENTE_SOCIAL':
            shape = "house"
        elif i in estamentos['ODONTOLOGO'] or s == 'ODONTOLOGO':
            shape = "trapezium"
        elif i in estamentos['PSICOLOGO/A'] or s == 'PSICOLOGO':
            shape = "diamond"
        elif i in estamentos['ADMINISTRADOR'] or i in estamentos['ADMINISTRATIVO'] or i in estamentos['SALA DE PROCEDIMIENTOS'] or s == 'ADMINISTRADOR' or s == 'ADMINISTRATIVO' or s == 'SALA DE PROCEDIMIENTOS':
            shape = "triangle"
        if i not in node2.keys():
            texto = texto + s + ' [label = "' + s +  '" shape = ' + shape + ' style = "filled" fillcolor = "#227722" fontcolor = ' + font + ']\n'
        else:
            y = float(abs(node1[i] - node2[i]))/min(node1[i], node2[i])
            #s = s +'_' +str(y)
            if y >= node_threshold:
                if node1[i] > node2[i]:
                    texto = texto + s + ' [label = "' + s +  '" shape = ' + shape + ' style = "filled" fillcolor = "#66CC66" fontcolor = ' + font + ']\n'
                elif node1[i] < node2[i]:
                    texto = texto + s + ' [label = "' + s +  '" shape = ' + shape + ' style = "filled" fillcolor = "#6666CC" fontcolor = ' + font + ']\n'
                else:
                    texto = texto + s + ' [label = "' + s +  '" shape = ' + shape + ' style = "filled" fillcolor = "#AAAAAA" fontcolor = ' + font + ']\n'
            else:
                lista_malos.append(i)
            del node2[i]

    for i in node2.keys():
        s = str(i).replace('-','')
        s = s.replace(' ','_')
        s = s.replace('_(C)','')
        s = s.replace('[S]_','')
        s = s.replace('+','_mas_')
        s = s.replace('(A)','A')
        s = s.replace('/A','')
        font = "white"
        shape = "none"
        if i in estamentos['MEDICO'] or s in ['MEDICO', 'MED_FAIL']:
            shape = "hexagon"
        elif i in estamentos['ENFERMERA'] or s in ['ENFERMERA', 'ENF_FAIL']:
            shape = "box"
        elif i in estamentos['MATRON(A)'] or s == 'MATRONA':
            shape = "circle"
        elif i in estamentos['KINESIOLOGO'] or s == 'KINESIOLOGO':
            shape = "octagon"
        elif i in estamentos['NUTRICIONISTA'] or s in ['NUTRICIONISTA', 'NUT_FAIL']:
            shape = "ellipse"
        elif i in estamentos['TECNICO PARAMEDICO'] or s == 'TECNICO PARAMEDICO':
            shape = "doublecircle"
        elif i in estamentos['ASISTENTE SOCIAL'] or s == 'ASISTENTE_SOCIAL':
            shape = "house"
        elif i in estamentos['ODONTOLOGO'] or s == 'ODONTOLOGO':
            shape = "trapezium"
        elif i in estamentos['PSICOLOGO/A'] or s == 'PSICOLOGO':
            shape = "diamond"
        elif i in estamentos['ADMINISTRADOR'] or i in estamentos['ADMINISTRATIVO'] or i in estamentos['SALA DE PROCEDIMIENTOS'] or s == 'ADMINISTRADOR' or s == 'ADMINISTRATIVO' or s == 'SALA DE PROCEDIMIENTOS':
            shape = "triangle"
        if i not in node1.keys():
            texto = texto + s + ' [label = ' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "#222277" fontcolor = ' + font + ']\n'

    for j in relation1.keys():
        if filter:
            if j not in differences:
                continue

        stroke = "2"
        arrow = "1"
        style = "solid"

        s1 = str(j[0]).replace('-','')
        s2 = str(j[1]).replace('-','')

        s1 = s1.replace(' ','_')
        s2 = s2.replace(' ','_')

        s1 = s1.replace('_(C)','')
        s2 = s2.replace('_(C)','')

        s1 = s1.replace('[S]_','')
        s2 = s2.replace('[S]_','')

        s1 = s1.replace('+','_mas_')
        s2 = s2.replace('+','_mas_')

        s1 = s1.replace('(A)','A')
        s2 = s2.replace('(A)','A')

        s1 = s1.replace('/A','')
        s2 = s2.replace('/A','')

        if len(j) == 2:
            if j[0] in lista_malos or j[1] in lista_malos:
                continue
            if j not in relation2:
                texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#227722" fontcolor = "yellow" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'

            else:
                x = float(abs(relation1[j] - relation2[j]))/min(relation1[j], relation2[j])
                style = "solid"
                if  x >= relation_threshold:
                    if relation1[j] > relation2[j]:
                        texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#66CC66" label = "'+ str(round(x,3)) + " " + '" fontcolor = "yellow" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'
                    elif relation1[j] < relation2[j]:
                        texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#6666CC" label = "'+ str(round(x,3)) + " " + '" fontcolor = "yellow" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'
                    else:
                        texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#AAAAAA" label = "'+ str(round(x,3)) + " " + '" fontcolor = "yellow" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'
                del relation2[j]

        elif len(j) == 3:
            if j[0] in lista_malos or j[1] in lista_malos or j[2] in lista_malos:
                continue
            s3 = str(j[2]).replace('-','')
            s3 = s3.replace(' ','_')
            s3 = s3.replace('_(C)','')
            s3 = s3.replace('[S]_','')
            s3 = s3.replace('+','_mas_')
            s3 = s3.replace('(A)','A')
            s3 = s3.replace('/A','')
            if s1 == s2 == s3:
                s1 = s1 + 'A'
                s2 = s2 + 'B'
                s3 = s3 + 'C'
            elif s1 == s2:
                s1 = s1 + 'A'
                s2 = s2 + 'B'
                s3 = s3[:len(s3)-1]
            elif s3 == s2:
                s2 = s2 + 'A'
                s3 = s3 + 'B'
                s1 = s1[:len(s1)-1]
            elif s1 == s3:
                s1 = s1 + 'A'
                s3 = s3 + 'B'
                s2 = s2[:len(s2)-1]

            else:
                s1 = s1[:len(s1)-1]
                s2 = s2[:len(s2)-1]
                s3 = s3[:len(s3)-1]

            if j not in relation2:
                texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#227722" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                texto = texto + s3 + '->' + s1 + '[arrowsize = '+ arrow + ' color = "#227722" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                texto = texto + s2 + '->' + s3 + '[arrowsize = '+ arrow + ' color = "#227722" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'

            else:
                x = float(abs(relation1[j] - relation2[j]))/min(relation1[j], relation2[j])
                if  x >= relation_threshold:
                    if relation1[j] > relation2[j]:
                        texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#66CC66" dir = "none" label = "'+ x + '" fontcolor = "orange" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s3 + '->' + s1 + '[arrowsize = '+ arrow + ' color = "#66CC66" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s2 + '->' + s3 + '[arrowsize = '+ arrow + ' color = "#66CC66" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                    elif relation1[j] < relation2[j]:
                        texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#6666CC" dir = "none" label = "'+ x + '" fontcolor = "orange" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s3 + '->' + s1 + '[arrowsize = '+ arrow + ' color = "#6666CC" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s2 + '->' + s3 + '[arrowsize = '+ arrow + ' color = "#6666CC" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                    else:
                        texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#AAAAAA" dir = "none" label = "'+ x + '" fontcolor = "orange" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s3 + '->' + s1 + '[arrowsize = '+ arrow + ' color = "#AAAAAA" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s2 + '->' + s3 + '[arrowsize = '+ arrow + ' color = "#AAAAAA" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                del relation2[j]
        elif len(j) == 4:
            if j[0] in lista_malos or j[1] in lista_malos or j[2] in lista_malos or j[3] in lista_malos:
                continue
            s4 = str(j[3]).replace('-','')
            s4 = s4.replace(' ','_')
            s4 = s4.replace('_(C)','')
            s4 = s4.replace('[S]_','')
            s4 = s4.replace('+','_mas_')
            s4 = s4.replace('(A)','A')
            s4 = s4.replace('/A','')

            if s1 == s2 == s3 == s4:
                s1 = s1 + 'A'
                s2 = s2 + 'B'
                s3 = s3 + 'C'
                s4 = s4 + 'D'
            elif s1 == s2 == s3:
                s1 = s1 + 'A'
                s2 = s2 + 'B'
                s3 = s3 + 'C'
                s4 = s4[:len(s4)-1]
            elif s1 == s2 == s4:
                s1 = s1 + 'A'
                s2 = s2 + 'B'
                s4 = s4 + 'C'
                s3 = s3[:len(s3)-1]
            elif s1 == s3 == s4:
                s1 = s1 + 'A'
                s3 = s3 + 'B'
                s4 = s4 + 'C'
                s2 = s2[:len(s2)-1]
            elif s2 == s3 == s4:
                s2 = s2 + 'A'
                s3 = s3 + 'B'
                s4 = s4 + 'C'
                s1 = s1[:len(s1)-1]

            elif s1 == s2 and s3 == s4:
                s1 = s1 + 'A'
                s2 = s2 + 'B'
                s3 = s3 + 'A'
                s4 = s4 + 'B'

            elif s1 == s3 and s2 == s4:
                s1 = s1 + 'A'
                s3 = s3 + 'B'
                s2 = s2 + 'A'
                s4 = s4 + 'B'

            elif s1 == s4 and s2 == s3:
                s1 = s1 + 'A'
                s4 = s4 + 'B'
                s2 = s2 + 'A'
                s3 = s3 + 'B'

            elif s1 == s2:
                s1 = s1 + 'A'
                s2 = s2 + 'B'
                s3 = s3[:len(s3)-1]
                s4 = s4[:len(s4)-1]
            elif s1 == s3:
                s1 = s1 + 'A'
                s3 = s3 + 'B'
                s2 = s2[:len(s2)-1]
                s4 = s4[:len(s4)-1]
            elif s1 == s4:
                s1 = s1 + 'A'
                s4 = s4 + 'B'
                s3 = s3[:len(s3)-1]
                s2 = s2[:len(s2)-1]
            elif s2 == s3:
                s2 = s2 + 'A'
                s3 = s3 + 'B'
                s1 = s1[:len(s1)-1]
                s4 = s4[:len(s4)-1]
            elif s2 == s4:
                s2 = s2 + 'A'
                s4 = s4 + 'B'
                s3 = s3[:len(s3)-1]
                s1 = s1[:len(s1)-1]
            elif s3 == s4:
                s3 = s3 + 'A'
                s4 = s4 + 'B'
                s1 = s1[:len(s1)-1]
                s2 = s2[:len(s2)-1]
            else:
                s1 = s1[:len(s1)-1]
                s2 = s2[:len(s2)-1]
                s3 = s3[:len(s3)-1]
                s4 = s4[:len(s4)-1]

            if j not in relation2:
                texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#227722" dir = "none" fontcolor = "red" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                texto = texto + s4 + '->' + s1 + '[arrowsize = '+ arrow + ' color = "#227722" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                texto = texto + s2 + '->' + s3 + '[arrowsize = '+ arrow + ' color = "#227722" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                texto = texto + s3 + '->' + s4 + '[arrowsize = '+ arrow + ' color = "#227722" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'

            else:
                x = float(abs(relation1[j] - relation2[j]))/min(relation1[j], relation2[j])
                if  x >= relation_threshold:
                    if relation1[j] > relation2[j]:
                        texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#66CC66" dir = "none" label = "'+ x + '" fontcolor = "red" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s4 + '->' + s1 + '[arrowsize = '+ arrow + ' color = "#66CC66" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s2 + '->' + s3 + '[arrowsize = '+ arrow + ' color = "#66CC66" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s3 + '->' + s4 + '[arrowsize = '+ arrow + ' color = "#66CC66" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'

                    elif relation1[j] < relation2[j]:
                        texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#6666CC" dir = "none" label = "'+ x + '" fontcolor = "red" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s4 + '->' + s1 + '[arrowsize = '+ arrow + ' color = "#6666CC" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s2 + '->' + s3 + '[arrowsize = '+ arrow + ' color = "#6666CC" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s3 + '->' + s4 + '[arrowsize = '+ arrow + ' color = "#6666CC" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'

                    else:
                        texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#AAAAAA" dir = "none" label = "'+ x + '" fontcolor = "red" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s4 + '->' + s1 + '[arrowsize = '+ arrow + ' color = "#AAAAAA" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s2 + '->' + s3 + '[arrowsize = '+ arrow + ' color = "#AAAAAA" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                        texto = texto + s3 + '->' + s4 + '[arrowsize = '+ arrow + ' color = "#AAAAAA" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'

                del relation2[j]


    for k in relation2.keys():
        if filter:
            if k not in differences:
                continue

        stroke = "2"
        arrow = "1"
        style = "solid"

        s1 = str(k[0]).replace('-','')
        s2 = str(k[1]).replace('-','')

        s1 = s1.replace(' ','_')
        s2 = s2.replace(' ','_')

        s1 = s1.replace('_(C)','')
        s2 = s2.replace('_(C)','')

        s1 = s1.replace('[S]_','')
        s2 = s2.replace('[S]_','')

        s1 = s1.replace('+','_mas_')
        s2 = s2.replace('+','_mas_')

        s1 = s1.replace('(A)','A')
        s2 = s2.replace('(A)','A')

        s1 = s1.replace('/A','')
        s2 = s2.replace('/A','')

        if len(k) == 2:
            if k[0] in lista_malos or k[1] in lista_malos:
                continue
            if k not in relation1.keys():
                texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#222277" fontcolor = "yellow" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'
        elif len(k) == 3:
            if k[0] in lista_malos or k[1] in lista_malos or k[2] in lista_malos:
                continue
            s3 = str(k[2]).replace('-','')
            s3 = s3.replace(' ','_')
            s3 = s3.replace('_(C)','')
            s3 = s3.replace('[S]_','')
            s3 = s3.replace('+','_mas_')
            s3 = s3.replace('(A)','A')
            s3 = s3.replace('/A','')
            if s1 == s2 == s3:
                s1 = s1 + 'A'
                s2 = s2 + 'B'
                s3 = s3 + 'C'
            elif s1 == s2:
                s1 = s1 + 'A'
                s2 = s2 + 'B'
                s3 = s3[:len(s3)-1]
            elif s3 == s2:
                s2 = s2 + 'A'
                s3 = s3 + 'B'
                s1 = s1[:len(s1)-1]
            elif s1 == s3:
                s1 = s1 + 'A'
                s3 = s3 + 'B'
                s2 = s2[:len(s2)-1]

            else:
                s1 = s1[:len(s1)-1]
                s2 = s2[:len(s2)-1]
                s3 = s3[:len(s3)-1]

            if k not in relation1.keys():
                texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#222277" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                texto = texto + s3 + '->' + s1 + '[arrowsize = '+ arrow + ' color = "#222277" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                texto = texto + s2 + '->' + s3 + '[arrowsize = '+ arrow + ' color = "#222277" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'

        elif len(k) == 4:
            if k[0] in lista_malos or k[1] in lista_malos or k[2] in lista_malos or k[3] in lista_malos:
                continue
            s4 = str(k[3]).replace('-','')
            s4 = s4.replace(' ','_')
            s4 = s4.replace('_(C)','')
            s4 = s4.replace('[S]_','')
            s4 = s4.replace('+','_mas_')
            s4 = s4.replace('(A)','A')
            s4 = s4.replace('/A','')

            if s1 == s2 == s3 == s4:
                s1 = s1 + 'A'
                s2 = s2 + 'B'
                s3 = s3 + 'C'
                s4 = s4 + 'D'
            elif s1 == s2 == s3:
                s1 = s1 + 'A'
                s2 = s2 + 'B'
                s3 = s3 + 'C'
                s4 = s4[:len(s4)-1]
            elif s1 == s2 == s4:
                s1 = s1 + 'A'
                s2 = s2 + 'B'
                s4 = s4 + 'C'
                s3 = s3[:len(s3)-1]
            elif s1 == s3 == s4:
                s1 = s1 + 'A'
                s3 = s3 + 'B'
                s4 = s4 + 'C'
                s2 = s2[:len(s2)-1]
            elif s2 == s3 == s4:
                s2 = s2 + 'A'
                s3 = s3 + 'B'
                s4 = s4 + 'C'
                s1 = s1[:len(s1)-1]

            elif s1 == s2 and s3 == s4:
                s1 = s1 + 'A'
                s2 = s2 + 'B'
                s3 = s3 + 'A'
                s4 = s4 + 'B'

            elif s1 == s3 and s2 == s4:
                s1 = s1 + 'A'
                s3 = s3 + 'B'
                s2 = s2 + 'A'
                s4 = s4 + 'B'

            elif s1 == s4 and s2 == s3:
                s1 = s1 + 'A'
                s4 = s4 + 'B'
                s2 = s2 + 'A'
                s3 = s3 + 'B'

            elif s1 == s2:
                s1 = s1 + 'A'
                s2 = s2 + 'B'
                s3 = s3[:len(s3)-1]
                s4 = s4[:len(s4)-1]
            elif s1 == s3:
                s1 = s1 + 'A'
                s3 = s3 + 'B'
                s2 = s2[:len(s2)-1]
                s4 = s4[:len(s4)-1]
            elif s1 == s4:
                s1 = s1 + 'A'
                s4 = s4 + 'B'
                s3 = s3[:len(s3)-1]
                s2 = s2[:len(s2)-1]
            elif s2 == s3:
                s2 = s2 + 'A'
                s3 = s3 + 'B'
                s1 = s1[:len(s1)-1]
                s4 = s4[:len(s4)-1]
            elif s2 == s4:
                s2 = s2 + 'A'
                s4 = s4 + 'B'
                s3 = s3[:len(s3)-1]
                s1 = s1[:len(s1)-1]
            elif s3 == s4:
                s3 = s3 + 'A'
                s4 = s4 + 'B'
                s1 = s1[:len(s1)-1]
                s2 = s2[:len(s2)-1]
            else:
                s1 = s1[:len(s1)-1]
                s2 = s2[:len(s2)-1]
                s3 = s3[:len(s3)-1]
                s4 = s4[:len(s4)-1]

            if k not in relation1.keys():
                texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#222277" dir = "none" fontcolor = "red" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                texto = texto + s4 + '->' + s1 + '[arrowsize = '+ arrow + ' color = "#222277" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                texto = texto + s2 + '->' + s3 + '[arrowsize = '+ arrow + ' color = "#222277" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'
                texto = texto + s3 + '->' + s4 + '[arrowsize = '+ arrow + ' color = "#222277" dir = "none" fontcolor = "yellow" fontsize = "12" style = "dashed" penwidth = '+ stroke + ']\n'



    texto = texto + '}'
    graf = Source(texto)
    #print (texto)

    filename = 'Graph-Output/Contrast_'+str(node_threshold)+'_'+str(relation_threshold)
    graf.render(filename, view=True)

def showExplicitContrast(node1, derivations1, avgannualder1, node2, derivations2, avgannualder2, node_threshold, relative_freq_threshold, absolute_freq_threshold):
    texto = 'digraph "Contraste" { rankdir=TB;\nnode [shape=box style = filled fillcolor = "#88FFFF"];\nbgcolor = "#6C6C6C";\nfontcolor = "white";\nlabel = "Relative relation contrast: \nNode Significance = ' + str(node_threshold) + '   Relation Significance = ' + str(relative_freq_threshold) + '";\nlabelloc = "t";\n'
    texto2 = 'digraph "Contraste" { rankdir=TB;\nnode [shape=box style = filled fillcolor = "#88FFFF"];\nbgcolor = "#6C6C6C";\nfontcolor = "white";\nlabel = "Annual average relation contrast: \nNode Significance = ' + str(node_threshold) + '   Relation Significance = ' + str(absolute_freq_threshold) + '";\nlabelloc = "t";\n'

    ignored_nodes = [] ###Nodos que no se toman en cuenta si aparecen en ambos logs pero la frecuencia es menor al threshold
    for i in node1.keys():
        s = str(i).replace('-','')
        s = s.replace(' ','_')
        s = s.replace('_(C)','')
        s = s.replace('[S]_','')
        s = s.replace('+','_mas_')
        s = s.replace('(A)','A')
        s = s.replace('/A','')
        font = "black"
        shape = "box"
        if s in ['MEDICO', 'MED_FAIL']:
            shape = "hexagon"
        elif s in ['ENFERMERA', 'ENF_FAIL']:
            shape = "box"
        elif s in ['NUTRICIONISTA', 'NUT_FAIL']:
            shape = "ellipse"

        if i not in node2.keys():
            texto = texto + s + ' [label = "' + s +  '" shape = ' + shape + ' style = "filled" fillcolor = "#227722" fontcolor = ' + font + ']\n'
            texto2 = texto2 + s + ' [label = "' + s +  '" shape = ' + shape + ' style = "filled" fillcolor = "#227722" fontcolor = ' + font + ']\n'

        else:
            y = float(abs(node1[i] - node2[i]))/min(node1[i], node2[i])
            #s = s +'_' +str(y)
            if y >= node_threshold:
                if node1[i] > node2[i]:
                    texto = texto + s + ' [label = "' + s +  '" shape = ' + shape + ' style = "filled" fillcolor = "#66CC66" fontcolor = ' + font + ']\n'
                    texto2 = texto2 + s + ' [label = "' + s +  '" shape = ' + shape + ' style = "filled" fillcolor = "#66CC66" fontcolor = ' + font + ']\n'

                elif node1[i] < node2[i]:
                    texto = texto + s + ' [label = "' + s +  '" shape = ' + shape + ' style = "filled" fillcolor = "#6666CC" fontcolor = ' + font + ']\n'
                    texto2 = texto2 + s + ' [label = "' + s +  '" shape = ' + shape + ' style = "filled" fillcolor = "#6666CC" fontcolor = ' + font + ']\n'

                else:
                    texto = texto + s + ' [label = "' + s +  '" shape = ' + shape + ' style = "filled" fillcolor = "#AAAAAA" fontcolor = ' + font + ']\n'
                    texto2 = texto2 + s + ' [label = "' + s +  '" shape = ' + shape + ' style = "filled" fillcolor = "#AAAAAA" fontcolor = ' + font + ']\n'

            else:
                ignored_nodes.append(i)
            del node2[i]

    for i in node2.keys():
        s = str(i).replace('-','')
        s = s.replace(' ','_')
        s = s.replace('_(C)','')
        s = s.replace('[S]_','')
        s = s.replace('+','_mas_')
        s = s.replace('(A)','A')
        s = s.replace('/A','')
        font = "white"
        shape = "none"
        if i in estamentos['MEDICO'] or s in ['MEDICO', 'MED_FAIL']:
            shape = "hexagon"
        elif i in estamentos['ENFERMERA'] or s in ['ENFERMERA', 'ENF_FAIL']:
            shape = "box"
        elif i in estamentos['NUTRICIONISTA'] or s in ['NUTRICIONISTA', 'NUT_FAIL']:
            shape = "ellipse"

        if i not in node1.keys():
            texto = texto + s + ' [label = ' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "#222277" fontcolor = ' + font + ']\n'
            texto2 = texto2 + s + ' [label = ' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "#222277" fontcolor = ' + font + ']\n'

    for j in list(derivations1.keys()):

        stroke = "2"
        arrow = "1"
        style = "solid"

        s1 = str(j[0]).replace('-','')
        s2 = str(j[1]).replace('-','')

        s1 = s1.replace(' ','_')
        s2 = s2.replace(' ','_')

        s1 = s1.replace('_(C)','')
        s2 = s2.replace('_(C)','')

        s1 = s1.replace('[S]_','')
        s2 = s2.replace('[S]_','')

        s1 = s1.replace('+','_mas_')
        s2 = s2.replace('+','_mas_')

        s1 = s1.replace('(A)','A')
        s2 = s2.replace('(A)','A')

        s1 = s1.replace('/A','')
        s2 = s2.replace('/A','')

        if j[0] in ignored_nodes or j[1] in ignored_nodes:
            continue
        if j not in derivations2:
            texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#227722" label = "abs freq: '+ str(round(derivations1[j],3)) + " " + '" fontcolor = "green" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'

        else:
            x = float(abs(derivations1[j] - derivations2[j]))/min(derivations1[j], derivations2[j])
            style = "solid"
            if  x >= relative_freq_threshold:
                x = x*100
                if derivations1[j] > derivations2[j]:
                    texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#66CC66" label = "'+ str(round(x,3)) + "% " + '" fontcolor = "yellow" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'
                elif derivations1[j] < derivations2[j]:
                    texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#6666CC" label = "'+ str(round(x,3)) + "% " + '" fontcolor = "yellow" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'
                else:
                    texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#AAAAAA" label = "'+ str(round(x,3)) + "% " + '" fontcolor = "yellow" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'
            del derivations2[j]

    for k in list(derivations2.keys()):

        stroke = "2"
        arrow = "1"
        style = "solid"

        s1 = str(k[0]).replace('-','')
        s2 = str(k[1]).replace('-','')

        s1 = s1.replace(' ','_')
        s2 = s2.replace(' ','_')

        s1 = s1.replace('_(C)','')
        s2 = s2.replace('_(C)','')

        s1 = s1.replace('[S]_','')
        s2 = s2.replace('[S]_','')

        s1 = s1.replace('+','_mas_')
        s2 = s2.replace('+','_mas_')

        s1 = s1.replace('(A)','A')
        s2 = s2.replace('(A)','A')

        s1 = s1.replace('/A','')
        s2 = s2.replace('/A','')
        if k[0] in ignored_nodes or k[1] in ignored_nodes:
            continue
        if k not in derivations1.keys():
            texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#222277" label = " abs freq: '+ str(round(derivations2[k],3)) + " " + '" fontcolor = "#222277" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'

    for j in list(avgannualder1.keys()):

        stroke = "2"
        arrow = "1"
        style = "solid"

        s1 = str(j[0]).replace('-','')
        s2 = str(j[1]).replace('-','')

        s1 = s1.replace(' ','_')
        s2 = s2.replace(' ','_')

        s1 = s1.replace('_(C)','')
        s2 = s2.replace('_(C)','')

        s1 = s1.replace('[S]_','')
        s2 = s2.replace('[S]_','')

        s1 = s1.replace('+','_mas_')
        s2 = s2.replace('+','_mas_')

        s1 = s1.replace('(A)','A')
        s2 = s2.replace('(A)','A')

        s1 = s1.replace('/A','')
        s2 = s2.replace('/A','')

        if j[0] in ignored_nodes or j[1] in ignored_nodes:
            continue
        if j not in avgannualder2:
            if avgannualder1[j] >= absolute_freq_threshold:
                texto2 = texto2 + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#227722" label = "'+ str(round(avgannualder1[j],3)) + " " + '" fontcolor = "green" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'

        else:
            y = float(abs(avgannualder1[j] - avgannualder2[j]))
            style = "solid"
            if  y >= absolute_freq_threshold:
                if avgannualder1[j] > avgannualder2[j]:
                    texto2 = texto2 + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#66CC66" label = "'+ str(round(y,3)) + " " + '" fontcolor = "yellow" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'
                elif avgannualder1[j] < avgannualder2[j]:
                    texto2 = texto2 + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#6666CC" label = "'+ str(round(y,3)) + " " + '" fontcolor = "yellow" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'
                else:
                    texto2 = texto2 + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#AAAAAA" label = "'+ str(round(y,3)) + " " + '" fontcolor = "yellow" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'
            del avgannualder2[j]

    for k in list(avgannualder2.keys()):

        stroke = "2"
        arrow = "1"
        style = "solid"

        s1 = str(k[0]).replace('-','')
        s2 = str(k[1]).replace('-','')

        s1 = s1.replace(' ','_')
        s2 = s2.replace(' ','_')

        s1 = s1.replace('_(C)','')
        s2 = s2.replace('_(C)','')

        s1 = s1.replace('[S]_','')
        s2 = s2.replace('[S]_','')

        s1 = s1.replace('+','_mas_')
        s2 = s2.replace('+','_mas_')

        s1 = s1.replace('(A)','A')
        s2 = s2.replace('(A)','A')

        s1 = s1.replace('/A','')
        s2 = s2.replace('/A','')
        if k[0] in ignored_nodes or k[1] in ignored_nodes:
            continue
        if k not in avgannualder1.keys():
            if avgannualder2[k] >= absolute_freq_threshold:
                texto2 = texto2 + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "#222277" label = "'+ str(round(avgannualder2[k],3)) + " " + '" fontcolor = "blue" fontsize = "12" style = ' + style + ' penwidth = '+ stroke + ']\n'


    texto = texto + '}'
    graf = Source(texto)
    filename = 'Graph-Output/RelationContrast_'+str(node_threshold)+'_'+str(relative_freq_threshold)
    graf.render(filename, view=True)

    texto2 = texto2 + '}'
    graf = Source(texto2)
    filename = 'Graph-Output/AnnualAvgContrast_'+str(node_threshold)+'_'+str(absolute_freq_threshold)
    graf.render(filename, view=True)


def showAll(Rimplicit, Rexplicit, freq_node, derivations, threshold, time, arrow_threshold, node_threshold, relation_threshold, less_info):
    global times
    if times == 0:
        bg = "#AA0066"
    else:
        bg = "#007766"
    bg = "#333333"
    texto = 'digraph "Interacciones" { rankdir=TB;\nconcentrate = true;\nnode [shape=box style = filled fillcolor = "#88FFFF"];\nbgcolor = "' + bg +'";\nfontcolor = "white";\nlabel = "All derivations: \nrelation threshold = ' + str(threshold) + '   time = ' + str(time) + '   derivation threshold = ' + str(arrow_threshold)  + '   node freq = ' + str(node_threshold)+ '   relation freq = ' + str(relation_threshold) +'";\nlabelloc = "t";\n'
    #print texto
    totalesImplicit = 0
    totalesExplicit = 0
    derivaciones = 0

    copia = dict(freq_node)

    raux = sorted(copia.items(), key=operator.itemgetter(1))
    daux = sorted(Rimplicit.items(), key=operator.itemgetter(1))

    file = 'Reports/Resource_frequency' + str(times) + '.txt'
    writer = open(file, 'w')
    for i in raux:
        if freq_node[str(i[0])] < node_threshold:
            del copia[str(i[0])]
            if less_info:
                continue
        writer.write(str(i[0]) + ':' + str(i[1]) + '\n')
    writer.write('\n\nSum: ' + str(np.sum(list(copia.values())))+'\nMean: ' + str(round(np.mean(list(copia.values())),3)) + '\nSD: ' + str(round(np.std(list(copia.values())),3)))
    writer.close()

    file = 'Reports/ID_Res_relation_frequency'+str(times)+'.txt'
    writer2= open(file, 'w')
    for i in daux:
        if freq_node[str(i[0][0])] < node_threshold or freq_node[str(i[0][1])] < node_threshold:
            del Rimplicit[(str(i[0][0]),str(i[0][1]))]
            if i[0][0] in derivations.keys():
                derivations[i[0][0]] -= i[1]
                if derivations[i[0][0]] == 0:
                    del derivations[i[0][0]]
                if less_info:
                    continue
        elif i[1] < relation_threshold:
            del Rimplicit[(str(i[0][0]),str(i[0][1]))]
            if i[0][0] in derivations.keys():
                derivations[i[0][0]] -= i[1]
                if derivations[i[0][0]] == 0:
                    del derivations[i[0][0]]
                if less_info:
                    continue
        writer2.write(str(i[0][0]) + '->' + str(i[0][1]) + ':' + str(i[1]) + '\n')
    writer2.write('\n\nSum: ' + str(np.sum(list(Rimplicit.values())))+'\nMean: ' + str(round(np.mean(list(Rimplicit.values())),3)) + '\nSD: ' + str(round(np.std(list(Rimplicit.values())),3)))
    writer2.close()

    dvaux = sorted(derivations.items(), key=operator.itemgetter(1))

    file = 'Reports/ID_Res_derivation_frequency'+str(times)+'.txt'
    writer3= open(file, 'w')
    for i in dvaux:
        if less_info:
            if freq_node[str(i[0])] < node_threshold:
                continue
        writer3.write(str(i[0]) + ':' + str(i[1]) + '\n')
    writer3.write('\n\nSum: ' + str(np.sum(list(derivations.values())))+'\nMean: ' + str(round(np.mean(list(derivations.values())),3)) + '\nSD: ' + str(round(np.std(list(derivations.values())),3)))
    writer3.close()

    for k in Rimplicit.keys():
        #if dic[k] >= total_threshold and lista[k[0]] >= freq_threshold and lista[k[1]] >= freq_threshold :
        totalesImplicit += Rimplicit[k]
    for k in derivations.keys():
        #if res_derivations[k] >= mean + sd and lista[k] >= freq_threshold:
        derivaciones += derivations[k]

    #print (totales, derivaciones)

    #lista['MEDICO'] = 10000
    #lista['ENFERMERA'] = 10000
    #lista['NUTRICIONISTA'] = 10000

    for k in Rexplicit.keys():
        if (Rexplicit[k] < relation_threshold):
            continue
        if freq_node[k[0]] < node_threshold:
            continue
        if str(k[1]) != 'MED' and str(k[1]) != 'ENF' and str(k[1]) != 'NUT':
            if freq_node[k[1]] < node_threshold:
                continue
        totalesExplicit += Rexplicit[k]

    for i in copia.keys():

        s = str(i).replace('-','')
        s = s.replace(' ','_')
        s = s.replace('_(C)','')
        s = s.replace('[S]_','')
        s = s.replace('+','_mas_')
        s = s.replace('(A)','A')
        s = s.replace('/A','')
        font = "white"
        shape = "none"
        if s == 'MEDICO':
            shape = "hexagon"
        elif s == 'ENFERMERA':
            shape = "box"
        elif s == 'MATRONA':
            shape = "circle"
        elif s == 'KINESIOLOGO':
            shape = "octagon"
        elif s == 'NUTRICIONISTA':
            shape = "ellipse"
        elif s == 'TECNICO PARAMEDICO':
            shape = "doublecircle"
        elif s == 'ASISTENTE_SOCIAL':
            shape = "house"
        elif s == 'ODONTOLOGO':
            shape = "trapezium"
        elif s == 'PSICOLOGO':
            shape = "diamond"
        elif s == 'ADMINISTRADOR' or s == 'ADMINISTRATIVO' or s == 'SALA DE PROCEDIMIENTOS':
            shape = "triangle"
        if(i in derivations.keys()):
            if(float(derivations[i])/derivaciones > arrow_threshold):
                font = "yellow"

        texto = texto + s + ' [label =' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "#990000" fontcolor = ' + font + ']\n'

    for j in Rimplicit.keys():
        if (Rimplicit[j] < relation_threshold):
            continue
        if(freq_node[str(j[0])] < node_threshold or freq_node[str(j[1])] < node_threshold):
            continue

        x = float(Rimplicit[j])/totalesImplicit
        x = round(x,3)
        if (x >= threshold):
            width = '  ' + str(x)
            stroke = str(8 * math.log(1 + x,2))
            arrow = str(2*(1/(2-x)))


            s1 = str(j[0]).replace('-','')
            s2 = str(j[1]).replace('-','')

            s1 = s1.replace(' ','_')
            s2 = s2.replace(' ','_')

            s1 = s1.replace('_(C)','')
            s2 = s2.replace('_(C)','')

            s1 = s1.replace('[S]_','')
            s2 = s2.replace('[S]_','')

            s1 = s1.replace('+','_mas_')
            s2 = s2.replace('+','_mas_')

            s1 = s1.replace('(A)','A')
            s2 = s2.replace('(A)','A')

            s1 = s1.replace('/A','')
            s2 = s2.replace('/A','')

            texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "blue" label = '+ width + ' fontsize = "30" fontcolor = "black" fontsize = "8" style = "solid" penwidth = '+ stroke + ']\n'
        else:
            del Rimplicit[j]
            continue

    for j in Rexplicit.keys():
        if (Rexplicit[j] < relation_threshold):
            continue
        if(freq_node[str(j[0])] < node_threshold):
            continue

        if (str(j[1]) != 'MED' and str(j[1]) != 'ENF' and str(j[1]) != 'NUT'):
            if freq_node[str(j[1])] < node_threshold:
                continue
        x = float(Rexplicit[j])/totalesExplicit
        x = round(x,3)
        if (x >= threshold):
            width = '  ' + str(x)
            stroke = str(8 * math.log(1 + x,2))
            arrow = str(2*(1/(2-x)))

            s1 = str(j[0]).replace('-','')
            s2 = str(j[1]).replace('-','')

            s1 = s1.replace(' ','_')
            s2 = s2.replace(' ','_')

            s1 = s1.replace('_(C)','')
            s2 = s2.replace('_(C)','')

            s1 = s1.replace('[S]_','')
            s2 = s2.replace('[S]_','')

            s1 = s1.replace('+','_mas_')
            s2 = s2.replace('+','_mas_')

            s1 = s1.replace('(A)','A')
            s2 = s2.replace('(A)','A')

            s1 = s1.replace('/A','')
            s2 = s2.replace('/A','')

            if (str(j[1]) != 'MED' and str(j[1]) != 'ENF' and str(j[1]) != 'NUT'):
                head = 'normal'
            else:
                head = 'tee'
                if str(j[1]) == 'MED':
                    s2 = 'MEDICO'
                elif str(j[1]) == 'ENF':
                    s2 = 'ENFERMERA'
                elif str(j[1]) == 'NUT':
                    s2 = 'NUTRICIONISTA'
            texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "white" label = '+ width + ' fontsize = "30" arrowhead = ' + head + ' fontcolor = "black" fontsize = "8" style = "dashed" penwidth = '+ stroke + ']\n'
        else:
            del Rexplicit[j]
            continue

    texto = texto + '}'
    graf = Source(texto)
    ###ARCHIVO EN FORMATO NOMBRE_THRESHOLD_TIME_ARROWTHRESHOLD.PDF

    filename = 'Graph-Output/ALL' + str(times)+'_'+str(threshold)+'_'+str(time)+'_'+str(arrow_threshold)+'_'+str(node_threshold)+'_'+str(relation_threshold)
    times += 1
    graf.render(filename, view=True)

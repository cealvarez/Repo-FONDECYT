import numpy as np
import operator
from graphviz import *
import math

def show_implicit_derivation(dic, lista, act_derivations, threshold, time, arrow_threshold, freq_threshold, total_threshold, less_info = False): #lista es diccionario
    texto = 'digraph "Interacciones" { rankdir=TB;\nconcentrate = true;\nbgcolor = "#333333";\nfontcolor = "white";\nlabel = "Implicit Derivation: \nrelation threshold = ' + str(threshold) + '   time = ' + str(time) + '   derivation threshold = ' + str(arrow_threshold)  + '   node freq = ' + str(freq_threshold)+ '   relation freq = ' + str(total_threshold) +'";\nlabelloc = "t";\n'
    totales = 0
    derivaciones = 0

    copia = dict(lista)
    raux = sorted(copia.items(), key=operator.itemgetter(1))

    ###LISTA QUE CONTIENE LAS ACTIVIDADES QUE NO PUEDEN SER TRIGGERS###
    lista_malos = []
    eventReader = open('Input/No_Triggers.txt', 'r')
    for line in eventReader:
        s = line.strip()
        lista_malos.append(s)

    daux = sorted(dic.items(), key=operator.itemgetter(1))


    writer = open('Reports/Activity_frequency.txt', 'w')
    for i in raux:
        if lista[str(i[0])] < freq_threshold:
            del copia[str(i[0])]
            if less_info:
                continue
        writer.write(str(i[0]) + ':' + str(i[1]) + '\n')
    writer.write('\n\nSum: ' + str(np.sum(copia.values()))+'\nMean: ' + str(round(np.mean(copia.values()),3)) + '\nSD: ' + str(round(np.std(copia.values()),3)))
    lmean = np.mean(copia.values())
    writer.close()

    writer2= open('Reports/Act_relation_frequency.txt', 'w')
    for i in daux:
        if lista[str(i[0][0])] < freq_threshold or lista[str(i[0][1])] < freq_threshold:
            del dic[(str(i[0][0]),str(i[0][1]))]
            if i[0][0] in act_derivations.keys():
                act_derivations[i[0][0]] -= i[1]
                if act_derivations[i[0][0]] == 0:
                    del act_derivations[i[0][0]]
                if less_info:
                    continue
        elif i[1] < total_threshold:
            del dic[(str(i[0][0]),str(i[0][1]))]
            if i[0][0] in act_derivations.keys():
                act_derivations[i[0][0]] -= i[1]
                if act_derivations[i[0][0]] == 0:
                    del act_derivations[i[0][0]]
                if less_info:
                    continue
        writer2.write(str(i[0][0]) + '->' + str(i[0][1]) + ':' + str(i[1]) + '\n')
    writer2.write('\n\nSum: ' + str(np.sum(dic.values()))+'\nMean: ' + str(round(np.mean(dic.values()),3)) + '\nSD: ' + str(round(np.std(dic.values()),3)))
    writer2.close()


    dvaux = sorted(act_derivations.items(), key=operator.itemgetter(1))

    writer3= open('Reports/Act_derivation_frequency.txt', 'w')
    for i in dvaux:
        if less_info:
            if lista[str(i[0])] < freq_threshold:
                continue
        writer3.write(str(i[0]) + ':' + str(i[1]) + '\n')
    writer3.write('\n\nSum: ' + str(np.sum(act_derivations.values()))+'\nMean: ' + str(round(np.mean(act_derivations.values()),3)) + '\nSD: ' + str(round(np.std(act_derivations.values()),3)))
    writer3.close()

    for k in dic.keys():
        #if dic[k] >= total_threshold and lista[k[0]] >= freq_threshold and lista[k[1]] >= freq_threshold :
        totales += dic[k]
    for k in act_derivations.keys():
        #if res_derivations[k] >= mean + sd and lista[k] >= freq_threshold:
        derivaciones += act_derivations[k]

    print (totales, derivaciones)

    for i in copia.keys():
        s = str(i).replace('-','')
        s = s.replace(' ','_')
        s = s.replace('_(C)','')
        s = s.replace('[S]_','')
        s = s.replace('+','_mas_')
        if(str(i) != 'nan'):
            shape = "hexagon"
            if(i not in lista_malos):
                if i in act_derivations.keys():
                    if(float(act_derivations[i])/derivaciones > arrow_threshold):
                        shape = "ellipse"
            if(copia[i] > lmean):
                texto = texto + s + ' [label =' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "#990000" fontcolor = "white"]\n'
            else:
                texto = texto + s + ' [label =' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "#006699" fontcolor = "white"]\n'
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

            texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "white" label = '+ width + ' fontsize = "30" fontcolor = "#33BB33" fontsize = "8" style = "solid" penwidth = '+ stroke + ']\n'
    texto = texto + '}'
    graf = Source(texto)
    ###ARCHIVO EN FORMATO NOMBRE_THRESHOLD_TIME_ARROWTHRESHOLD.PDF
    filename = 'Graph-Output/ID_'+str(threshold)+'_'+str(time)+'_'+str(arrow_threshold)+str(freq_threshold)+'_'+str(total_threshold)
    graf.render(filename, view=True)

def show_implicit_derivation_role(dic, lista, res_derivations, estamentos, threshold, time, arrow_threshold, freq_threshold, total_threshold, less_info = False): #lista es diccionario
    texto = 'digraph "Interacciones" { rankdir=TB;\nconcentrate = true;\nbgcolor = "#333333";\nfontcolor = "white";\nlabel = "Implicit Derivation: \nrelation threshold = ' + str(threshold) + '   time = ' + str(time) + '   derivation threshold = ' + str(arrow_threshold)  + '   node freq = ' + str(freq_threshold)+ '   relation freq = ' + str(total_threshold) +'";\nlabelloc = "t";\n'
    totales = 0
    derivaciones = 0

    copia = dict(lista)

    raux = sorted(copia.items(), key=operator.itemgetter(1))
    daux = sorted(dic.items(), key=operator.itemgetter(1))

    writer = open('Reports/Resource_frequency.txt', 'w')
    for i in raux:
        if lista[str(i[0])] < freq_threshold:
            del copia[str(i[0])]
            if less_info:
                continue
        writer.write(str(i[0]) + ':' + str(i[1]) + '\n')
    writer.write('\n\nSum: ' + str(np.sum(copia.values()))+'\nMean: ' + str(round(np.mean(copia.values()),3)) + '\nSD: ' + str(round(np.std(copia.values()),3)))
    writer.close()

    lmean = np.mean(copia.values())

    writer2= open('Reports/Res_relation_frequency.txt', 'w')
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
    writer2.write('\n\nSum: ' + str(np.sum(dic.values()))+'\nMean: ' + str(round(np.mean(dic.values()),3)) + '\nSD: ' + str(round(np.std(dic.values()),3)))
    writer2.close()

    dvaux = sorted(res_derivations.items(), key=operator.itemgetter(1))

    writer3= open('Reports/Res_derivation_frequency.txt', 'w')
    for i in dvaux:
        if less_info:
            if lista[str(i[0])] < freq_threshold:
                continue
        writer3.write(str(i[0]) + ':' + str(i[1]) + '\n')
    writer3.write('\n\nSum: ' + str(np.sum(res_derivations.values()))+'\nMean: ' + str(round(np.mean(res_derivations.values()),3)) + '\nSD: ' + str(round(np.std(res_derivations.values()),3)))
    writer3.close()

    for k in dic.keys():
        #if dic[k] >= total_threshold and lista[k[0]] >= freq_threshold and lista[k[1]] >= freq_threshold :
        totales += dic[k]
    for k in res_derivations.keys():
        #if res_derivations[k] >= mean + sd and lista[k] >= freq_threshold:
        derivaciones += res_derivations[k]

    print (totales, derivaciones)

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
        if i in estamentos['MEDICO'] or s == 'MEDICO':
            shape = "hexagon"
        elif i in estamentos['ENFERMERA'] or s == 'ENFERMERA':
            shape = "box"
        elif i in estamentos['MATRON(A)'] or s == 'MATRONA':
            shape = "circle"
        elif i in estamentos['KINESIOLOGO'] or s == 'KINESIOLOGO':
            shape = "octagon"
        elif i in estamentos['NUTRICIONISTA'] or s == 'NUTRICIONISTA':
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
        if(i in res_derivations.keys()):
            if(float(res_derivations[i])/derivaciones > arrow_threshold and i not in estamentos['ADMINISTRADOR'] and i not in estamentos['ADMINISTRATIVO'] and i not in estamentos['SALA DE PROCEDIMIENTOS'] ):
                font = "yellow"
        if(copia[i] > lmean):
            texto = texto + s + ' [label =' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "#990000" fontcolor = ' + font + ']\n'
        else:
            texto = texto + s + ' [label =' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "#006699" fontcolor = ' + font + ']\n'
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

            texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "white" label = '+ width + ' fontsize = "30" fontcolor = "#33BB33" fontsize = "8" style = "solid" penwidth = '+ stroke + ']\n'
    texto = texto + '}'
    graf = Source(texto)
    ###ARCHIVO EN FORMATO NOMBRE_THRESHOLD_TIME_ARROWTHRESHOLD.PDF
    filename = 'Graph-Output/ID_'+str(threshold)+'_'+str(time)+'_'+str(arrow_threshold)+'_'+str(freq_threshold)+'_'+str(total_threshold)
    graf.render(filename, view=True)

def showDuo(dic, lista, estamentos, threshold, freq_threshold, total_threshold, time):
    texto = 'digraph "Interacciones" { rankdir=TB;\nconcentrate = true;\nbgcolor = "#333333";\nfontcolor = "white";\nlabel = "Duo: \nrelation threshold = ' + str(threshold) + '   time = ' + str(time) + '   node freq = ' + str(freq_threshold)+ '   relation freq = ' + str(total_threshold) +'";\nlabelloc = "t";\n'
    totales = 0
    mean = np.mean(list(lista.values()))

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
        shape = "none"
        if i in estamentos['MEDICO'] or s == 'MEDICO':
            shape = "hexagon"
        elif i in estamentos['ENFERMERA'] or s == 'ENFERMERA':
            shape = "box"
        elif i in estamentos['MATRON(A)'] or s == 'MATRONA':
            shape = "circle"
        elif i in estamentos['KINESIOLOGO'] or s == 'KINESIOLOGO':
            shape = "octagon"
        elif i in estamentos['NUTRICIONISTA'] or s == 'NUTRICIONISTA':
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

        if(lista[i] > mean):
            texto = texto + s + ' [label =' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "#990000" fontcolor = ' + font + ']\n'
        else:
            texto = texto + s + ' [label =' + s +  ' shape = ' + shape + ' style = "filled" fillcolor = "#006699" fontcolor = ' + font + ']\n'
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

            texto = texto + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "white" dir = "none" label = '+ width + ' fontsize = "30" fontcolor = "#33BB33" fontsize = "8" style = "solid" penwidth = '+ stroke + ']\n'
    texto = texto + '}'
    graf = Source(texto)
    ###ARCHIVO EN FORMATO NOMBRE_THRESHOLD_TIME_ARROWTHRESHOLD.PDF
    filename = 'Graph-Output/Duo_'+str(threshold)+'_'+str(time)+'_'+str(freq_threshold)+'_'+str(total_threshold)
    graf.render(filename, view=True)

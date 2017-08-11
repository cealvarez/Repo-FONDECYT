import operator
from graphviz import *
import math

times = 0

color_scale = ["#BBBBFF", "#AAAAFF", "#9999FF", "#8888FF", "#7777FF", "#6666FF", "#4444FF", "#2222FF", "#1111FF", "#0000FF"]
edge_scale = ["#F00000", "#F00000", "#F02800", "#F06800", "#F0A800", "#F2F000", "#81E400", "#35E400", "#08E400", "#08E400"]

def run_adherence(file, lab):
    referrals = {}
    mean_adherence = {}
    reader = open(file, 'r')
    reader.readline()
    for line in reader:
        lista = line.strip().split(';')
        referrals[lista[0]] = {}
        referrals[lista[0]][('MEDICO', 'MEDICO')] = [lista[1], lista[2]]
        referrals[lista[0]][('MEDICO', 'ENFERMERA')] = [lista[3], lista[4]]
        referrals[lista[0]][('MEDICO', 'NUTRICIONISTA')] = [lista[5], lista[6]]
        referrals[lista[0]][('ENFERMERA', 'MEDICO')] = [lista[7], lista[8]]
        referrals[lista[0]][('ENFERMERA', 'ENFERMERA')] = [lista[9], lista[10]]
        referrals[lista[0]][('ENFERMERA', 'NUTRICIONISTA')] = [lista[11], lista[12]]
        referrals[lista[0]][('NUTRICIONISTA', 'MEDICO')] = [lista[13], lista[14]]
        referrals[lista[0]][('NUTRICIONISTA', 'ENFERMERA')] = [lista[15], lista[16]]
        referrals[lista[0]][('NUTRICIONISTA', 'NUTRICIONISTA')] = [lista[17], lista[18]]

        mean_adherence[lista[0]] = {}
        mean_adherence[lista[0]][('MEDICO', 'MEDICO')] = lista[19]
        mean_adherence[lista[0]][('MEDICO', 'ENFERMERA')] = lista[20]
        mean_adherence[lista[0]][('MEDICO', 'NUTRICIONISTA')] = lista[21]
        mean_adherence[lista[0]][('ENFERMERA', 'MEDICO')] = lista[22]
        mean_adherence[lista[0]][('ENFERMERA', 'ENFERMERA')] = lista[23]
        mean_adherence[lista[0]][('ENFERMERA', 'NUTRICIONISTA')] = lista[24]
        mean_adherence[lista[0]][('NUTRICIONISTA', 'MEDICO')] = lista[25]
        mean_adherence[lista[0]][('NUTRICIONISTA', 'ENFERMERA')] = lista[26]
        mean_adherence[lista[0]][('NUTRICIONISTA', 'NUTRICIONISTA')] = lista[27]

    reader.close()
    showExplicitDerivation(referrals, mean_adherence, lab)


def showExplicitDerivation(referrals, mean_adherence, lab):
    global color_scale

    bg_adherence = "#646464"
    label1 = "Adherence " + lab

    texto1 = 'digraph "Interacciones" { rankdir=TB;\nconcentrate = true;\nbgcolor = "'+ bg_adherence + '";\nfontcolor = "white";\nlabel = "' + label1 + '. Derivations: Sample: '+ str(len(referrals.keys())) + '";\nlabelloc = "t";\n'

    texto1 = texto1 + "MEDICO" + ' [label =' + "MEDICO" +  ' shape = ' + "hexagon" + ' style = "filled" fillcolor = "'+ color_scale[4] +'" fontcolor = ' + "black" + ']\n'
    texto1 = texto1 + "ENFERMERA" + ' [label =' + "ENFERMERA" +  ' shape = ' + "box" + ' style = "filled" fillcolor = "'+ color_scale[4] +'" fontcolor = ' + "black" + ']\n'
    texto1 = texto1 + "NUTRICIONISTA" + ' [label =' + "NUTRICIONISTA" +  ' shape = ' + "ellipse" + ' style = "filled" fillcolor = "'+ color_scale[4] +'" fontcolor = ' + "black" + ']\n'

    adherence = {}
    adherence[('MEDICO', 'MEDICO')] = [0,0]
    adherence[('MEDICO', 'ENFERMERA')] = [0,0]
    adherence[('MEDICO', 'NUTRICIONISTA')] = [0,0]
    adherence[('ENFERMERA', 'MEDICO')] = [0,0]
    adherence[('ENFERMERA', 'ENFERMERA')] = [0,0]
    adherence[('ENFERMERA', 'NUTRICIONISTA')] = [0,0]
    adherence[('NUTRICIONISTA', 'MEDICO')] = [0,0]
    adherence[('NUTRICIONISTA', 'ENFERMERA')] = [0,0]
    adherence[('NUTRICIONISTA', 'NUTRICIONISTA')] = [0,0]

    for p in referrals:
        for t in referrals[p]:
            adherence[t][0] += int(referrals[p][t][0])
            adherence[t][1] += int(referrals[p][t][1])

    for t in adherence:
        s1 = t[0]
        s2 = t[1]
        absolute_freq = adherence[t][1]
        if adherence[t][1] > 0:
            x = round(adherence[t][0]/float(adherence[t][1]),4)
        else:
            x = 0
        width = ' ' + str(round(x*100, 2)) + '%, ' + str(absolute_freq)
        stroke = str(2.8 * math.log(1.25 + x,2))
        arrow = str(1*(1/(2-x)))
        head = 'normal'
        color_pos = int(x * 10)
        if color_pos > 9:
            color_pos = 9
        color = edge_scale[color_pos]
        texto1 = texto1 + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "' + color + '" label = "'+ width + '" arrowhead = ' + head + ' fontcolor = "white" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'

    texto1 = texto1 + '}'
    graf = Source(texto1)
    ###ARCHIVO EN FORMATO NOMBRE_THRESHOLD_TIME_ARROWTHRESHOLD.PDF
    filename = 'Adherencia/Grafos/Total'
    graf.render(filename, view=True)





    ##ADHERENCIA PROMEDIO###

    label2 = "Mean Adherence " + lab
    texto2 = 'digraph "Interacciones" { rankdir=TB;\nconcentrate = true;\nbgcolor = "'+ bg_adherence + '";\nfontcolor = "white";\nlabel = "' + label2 + '. Derivations: Sample: '+ str(len(referrals.keys())) + '";\nlabelloc = "t";\n'

    texto2 = texto2 + "MEDICO" + ' [label =' + "MEDICO" +  ' shape = ' + "hexagon" + ' style = "filled" fillcolor = "'+ color_scale[4] +'" fontcolor = ' + "black" + ']\n'
    texto2 = texto2 + "ENFERMERA" + ' [label =' + "ENFERMERA" +  ' shape = ' + "box" + ' style = "filled" fillcolor = "'+ color_scale[4] +'" fontcolor = ' + "black" + ']\n'
    texto2 = texto2 + "NUTRICIONISTA" + ' [label =' + "NUTRICIONISTA" +  ' shape = ' + "ellipse" + ' style = "filled" fillcolor = "'+ color_scale[4] +'" fontcolor = ' + "black" + ']\n'

    count_ad = {}
    sum_ad = {}
    sum_ad[('MEDICO', 'MEDICO')] = 0
    sum_ad[('MEDICO', 'ENFERMERA')] = 0
    sum_ad[('MEDICO', 'NUTRICIONISTA')] = 0
    sum_ad[('ENFERMERA', 'MEDICO')] = 0
    sum_ad[('ENFERMERA', 'ENFERMERA')] = 0
    sum_ad[('ENFERMERA', 'NUTRICIONISTA')] = 0
    sum_ad[('NUTRICIONISTA', 'MEDICO')] = 0
    sum_ad[('NUTRICIONISTA', 'ENFERMERA')] = 0
    sum_ad[('NUTRICIONISTA', 'NUTRICIONISTA')] = 0

    count_ad[('MEDICO', 'MEDICO')] = 0
    count_ad[('MEDICO', 'ENFERMERA')] = 0
    count_ad[('MEDICO', 'NUTRICIONISTA')] = 0
    count_ad[('ENFERMERA', 'MEDICO')] = 0
    count_ad[('ENFERMERA', 'ENFERMERA')] = 0
    count_ad[('ENFERMERA', 'NUTRICIONISTA')] = 0
    count_ad[('NUTRICIONISTA', 'MEDICO')] = 0
    count_ad[('NUTRICIONISTA', 'ENFERMERA')] = 0
    count_ad[('NUTRICIONISTA', 'NUTRICIONISTA')] = 0

    for p in mean_adherence:
        for t in mean_adherence[p]:
            if float(mean_adherence[p][t]) != -1:
                sum_ad[t] += float(mean_adherence[p][t])
                count_ad[t] += 1

    print(sum_ad)
    for t in sum_ad:
        s1 = t[0]
        s2 = t[1]
        total_patients = count_ad[t]
        if total_patients > 0:
            x = round(sum_ad[t]/float(count_ad[t]),4)
        else:
            x = 0
        width = ' ' + str(round(x*100, 2)) + '%, ' + str(count_ad[t])
        stroke = str(2.8 * math.log(1.25 + x,2))
        arrow = str(1*(1/(2-x)))
        head = 'normal'
        color_pos = int(x * 10)
        if color_pos > 9:
            color_pos = 9
        color = edge_scale[color_pos]
        texto2 = texto2 + s1 + '->' + s2 + '[arrowsize = '+ arrow + ' color = "' + color + '" label = "'+ width + '" arrowhead = ' + head + ' fontcolor = "white" fontsize = "12" style = "solid" penwidth = '+ stroke + ']\n'

    texto2 = texto2 + '}'
    graf = Source(texto2)
    ###ARCHIVO EN FORMATO NOMBRE_THRESHOLD_TIME_ARROWTHRESHOLD.PDF
    filename2 = 'Adherencia/Grafos/Mean_' + lab
    graf.render(filename2, view=True)

l = 'SAH'
run_adherence('Adherencia/A_' + l +'.csv', l)
__author__ = 'Camilo'

import numpy as np
import pylab as pl
from scipy.stats import t, norm, f
import operator

chi_table = {}
###FORMATO GL,CONFIANZA
chi_table[(1,0.005)] = 0.0000393
chi_table[(1,0.01)] = 0.0001571
chi_table[(1,0.025)] = 0.0009821
chi_table[(1,0.05)] = 0.0039321
chi_table[(1,0.1)] = 0.0157908
chi_table[(1,0.9)] = 2.70554
chi_table[(1,0.95)] = 3.84146
chi_table[(1,0.975)] = 5.02389
chi_table[(1,0.99)] = 6.63490
chi_table[(1,0.995)] = 7.87944

chi_table[(2,0.9)] = 4.60517
chi_table[(2,0.95)] = 5.99147
chi_table[(2,0.975)] = 7.37776
chi_table[(2,0.99)] = 9.21034
chi_table[(2,0.995)] = 10.5966

chi_table[(3,0.9)] = 6.25139
chi_table[(3,0.95)] = 7.81473
chi_table[(3,0.975)] = 9.34840
chi_table[(3,0.99)] = 11.3449
chi_table[(3,0.995)] = 12.8381

chi_table[(4,0.9)] = 7.77944
chi_table[(4,0.95)] = 9.48773
chi_table[(4,0.975)] = 11.1433
chi_table[(4,0.99)] = 13.2767
chi_table[(4,0.995)] = 14.8602

chi_table[(5,0.9)] = 9.23635
chi_table[(5,0.95)] = 11.0705
chi_table[(5,0.975)] = 12.8325
chi_table[(5,0.99)] = 15.0863
chi_table[(5,0.995)] = 16.7496

chi_table[(6,0.9)] = 10.6446
chi_table[(6,0.95)] = 12.5916
chi_table[(6,0.975)] = 14.4494
chi_table[(6,0.99)] = 16.8119
chi_table[(6,0.995)] = 18.5476

chi_table[(7,0.9)] = 12.0170
chi_table[(7,0.95)] = 14.0671
chi_table[(7,0.975)] = 16.0128
chi_table[(7,0.99)] = 18.4753
chi_table[(7,0.995)] = 20.2777

chi_table[(8,0.9)] = 13.3616
chi_table[(8,0.95)] = 15.5073
chi_table[(8,0.975)] = 17.5346
chi_table[(8,0.99)] = 20.0902
chi_table[(8,0.995)] = 21.9550

chi_table[(9,0.9)] = 14.6837
chi_table[(9,0.95)] = 16.9190
chi_table[(9,0.975)] = 19.0228
chi_table[(9,0.99)] = 21.6660
chi_table[(9,0.995)] = 23.5893

chi_table[(10,0.9)] = 15.9871
chi_table[(10,0.95)] = 18.3070
chi_table[(10,0.975)] = 20.4831
chi_table[(10,0.99)] = 23.2093
chi_table[(10,0.995)] = 15.1882



first_log_data = []
second_log_data = []

times = 0

###PARA AGREGAR LOS DICCIONARIOS A LAS LISTAS CORRESPONDIENTES

def first_add_data(dict, name, qty, relation):
    first_log_data.append((dict, name, qty, relation))
def second_add_data(dict, name, qty, relation):
    second_log_data.append((dict, name, qty, relation))

###TEST CHI CUADRADO. RETORNA UNA LISTA DE RELACIONES LAS CUALES SU FRECUENCIA DEPENDE DEL LOG
def chisq (confidence):
    global first_log_data
    global second_log_data
    global chi_table
    global times

    effective_relations = []

    for i in range(len(first_log_data)):
        obs1 = first_log_data[i][0]
        obs2 = second_log_data[i][0]
        name1 = first_log_data[i][1]
        name2 = second_log_data[i][1]
        n1 = first_log_data[i][2]
        n2 = second_log_data[i][2]
        relation = first_log_data[i][3]

        for i in obs1.keys():
            if i not in obs2.keys():
                obs2[i] = 0
        for i in obs2.keys():
            if i not in obs1.keys():
                obs1[i] = 0
        columns = {}
        for i in obs1.keys():
            columns[i] = obs1[i] + obs2[i]
        expected1 = {}
        expected2 = {}
        for i in obs1.keys():
            expected1[i] = float(columns[i]) * n1 /(n1 + n2)
            expected2[i] = float(columns[i]) * n2 /(n1 + n2)
        x = 0
        for i in obs1.keys():
            x += (obs1[i] - expected1[i])**2 / expected1[i]
        for i in obs2.keys():
            x += (obs2[i] - expected2[i])**2 / expected2[i]

        df = len(obs1.keys()) - 1
        x = round(x,5)
        if df == 0:
            continue

        elif x > chi_table[(df, confidence)]:
            writer = open("Reports/Statistics/Chisq" + str(times) + ".txt", "w")
            writer.write("CHI SQUARE TEST FOR " + str(relation) + " \n\n")
            writer.write("\t\t\t\t\t")
            off1 = (20 - len(name1))//4 + 1
            off2 = (20 - len(name2))//4 + 1
            for column in sorted(obs1.keys()):
                writer.write(str(column) + "\t\t\t")
            writer.write("\n" + name1 + "\t"*off1)
            for i in sorted(obs1.keys()):
                writer.write(str(obs1[i]) + "\t\t\t")
            writer.write("\n" + name2 + "\t"*off2)
            for i in sorted(obs2.keys()):
                writer.write(str(obs2[i]) + "\t\t\t")
            writer.write("\n\ndegrees of freedom: "+ str(df) + "\nx = " + str(x) + "\n")
            times += 1

            effective_relations.append(relation)
            writer.write(str(list(obs1.keys())) + " depend on [" + name1 + ', ' + name2 + "] with " + str(float(confidence) * 100) + "% of confidence")
            ###SE RECHAZA H0
            writer.close()
    return effective_relations

def indepence_test(file, confidence):
    reader = open(file, "r")
    label1 = []
    label2 = []
    reader.readline()
    data = {}
    for line in reader:
        lista = line.strip().split(';')
        data[lista[0]] = [lista[1], lista[2]]
        if lista[1] not in label1:
            label1.append(lista[1])
        if lista[2] not in label2:
            label2.append(lista[2])

    print(label1)
    print(label2)

    independence(label1, label2, data, confidence)

#{ID: [HBA1C, ADHERENCE]}
def independence(label1, label2, data, confidence):

    observed_dic = {}
    expected_dic = {}
    chisq_estimator = 0

    #Setting observed dic
    for i in label1:
        for j in label2:
            observed_dic[(i,j)] = 0

    #Computing observed dic
    for k in data:
        observed_dic[(data[k][0],data[k][1])] += 1

    #Computing expected dic
    for i in label1:
        for j in label2:
            sum1 = 0
            sum2 = 0
            for k in label2:
                sum1 += observed_dic[(i,k)]
            for k in label1:
                sum2 += observed_dic[(k,j)]
            expected_dic[(i,j)] = sum1*sum2 / len(data)

    #Computing estimator
    for i in label1:
        for j in label2:
            print(observed_dic[(i,j)], expected_dic[(i,j)], (observed_dic[(i,j)] - expected_dic[(i,j)])**2 / expected_dic[(i,j)])
            chisq_estimator += (observed_dic[(i,j)] - expected_dic[(i,j)])**2 / expected_dic[(i,j)]

    df = (len(label1) - 1) * (len(label2) - 1)
    print(chisq_estimator, df)

    if df == 0:
        print ("Grados de libertad = 0")

    elif chisq_estimator > chi_table[(df, confidence)]:
        print ("Son dependientes")

    else:
        print("Son independientes")

def t_test(sample1, sample2, confidence):
    print ('Medias:', np.mean(sample1), np.mean(sample2))
    #print ('Varianzas:', np.var(sample1, ddof = 1), np.var(sample2, ddof = 1))
    #print ('Muestra:', len(sample1), len(sample2))
    
    if len(sample1) <= 1 or len(sample2) <= 1:
        return "-"
    ddof1 = 1
    ddof2 = 1
    if len(sample1) == 1:
        ddof1 = 0
    if len(sample2) == 1:
        ddof2 = 0

    significance = 1 - confidence
    if var_test(sample1, sample2, confidence):
        sp = (((len(sample1)-1)*np.var(sample1, ddof = ddof1)+(len(sample2)-1)*np.var(sample2, ddof = ddof2))/(len(sample1)+len(sample2)-2))**0.5
        #print(sp)
        z = (abs(np.mean(sample1) - np.mean(sample2)))/(sp * (1/len(sample1) + 1/len(sample2))**0.5)
        df = len(sample1) + len(sample2) - 2
        t_statistic = t.ppf(significance/2, df)
        ic_min = (np.mean(sample1) - np.mean(sample2)) + t_statistic * (1/len(sample1) + 1/len(sample2))**0.5 * sp
        ic_max = (np.mean(sample1) - np.mean(sample2)) - t_statistic * (1/len(sample1) + 1/len(sample2))**0.5 * sp
        #print(t.ppf(significance/2, df) * (1/len(sample1) + 1/len(sample2))**0.5 * sp)
    else:
        sp = (np.var(sample1, ddof = ddof1)/len(sample1) + np.var(sample2, ddof = ddof2)/len(sample2))**0.5
        z = (abs(np.mean(sample1) - np.mean(sample2)))/sp
        #df = ((np.var(sample1)/len(sample1) + np.var(sample2)/len/sample2)**2)/(((np.var(sample1)/len(sample1))**2)/(len(sample1)-1) + ((np.var(sample2)/len(sample2))**2)/(len(sample2)-1))
        df = int((np.var(sample1, ddof = ddof1)/len(sample1) + np.var(sample2, ddof = ddof2)/len(sample2))**2/(((np.var(sample1, ddof = ddof1)/len(sample1))**2)/(len(sample1)+1) + ((np.var(sample2, ddof = ddof2)/len(sample2))**2)/(len(sample2)+1))) - 2
        #print((np.var(sample1, ddof = 1)/len(sample1) + np.var(sample2, ddof = 1))
        t_statistic = t.ppf(significance/2, df)
        ic_min = (np.mean(sample1) - np.mean(sample2)) + t_statistic * sp
        ic_max = (np.mean(sample1) - np.mean(sample2)) - t_statistic * sp
        #print(t.ppf(significance/2, df) * sp)
    
    p_value = 1 - t.cdf(z, df)
    #print (z, df, -1*t_statistic)
    #print ('P-VALUE: ', 100*p_value, '%', 'SIGNIFICANCE:', 50*significance, '%')
    #print(ic_min, ic_max)
    return str(round(100*p_value,3)) + '%'

    '''
    if z <= -1*t_statistic:
        print ('t: No se rechaza H0. Las muestras son iguales')
    else:
        print ('t: Se rechaza H0. Las muestras son diferentes')
    if p_value >= significance/2:
        print ('t: No se rechaza H0. Las muestras son iguales')
    else:
        print ('t: Se rechaza H0. Las muestras son diferentes')
    if ic_min < 0 < ic_max:
        print ('t: No se rechaza H0. Las muestras son iguales')
    else:
        print ('t: Se rechaza H0. Las muestras son diferentes')
    '''
    
def normal_test(sample1, sample2, confidence):
    print ('Medias:', np.mean(sample1), np.mean(sample2))
    #print ('Varianzas:', np.var(sample1, ddof = 1), np.var(sample2, ddof = 1))
    #print ('Muestra:', len(sample1), len(sample2))
    p_value = (abs(np.mean(sample1) - np.mean(sample2)))/(np.var(sample1)/len(sample1) + np.var(sample2)/len(sample2))*0.5
    print ('P-VALUE: ', 2*(1 - norm.cdf(p_value)))
    ic_min = abs(np.mean(sample1) - np.mean(sample2)) - norm.ppf(0.995) * (np.var(sample1)/len(sample1) + np.var(sample2)/len(sample2))*0.5
    ic_max = abs(np.mean(sample1) - np.mean(sample2)) + norm.ppf(0.995) * (np.var(sample1)/len(sample1) + np.var(sample2)/len(sample2))*0.5
    print(ic_min, ic_max)
    if ic_min < 0 < ic_max:
        print ('Norm: No se rechaza H0. Las muestras son iguales')
    else:
        print ('Norm: se rechaza H0. Las muestras son diferentes')

def var_test(sample1, sample2, confidence):
    if np.var(sample1, ddof = 1) > np.var(sample2, ddof = 1):
        s1 = np.var(sample1, ddof = 1)
        s2 = np.var(sample2, ddof = 1)
        n1 = len(sample1)
        n2 = len(sample2)
    else:
        s1 = np.var(sample2, ddof = 1)
        s2 = np.var(sample1, ddof = 1)
        n1 = len(sample2)
        n2 = len(sample1)
    z = (1-confidence)/2
    ic_min = s1/s2 * f.ppf(z, n2-1, n1-1)
    ic_max = s1/s2 * f.ppf(1-z, n2-1, n1-1)
    if ic_min < 1 < ic_max:
        #print ('same vars')
        return True
    else:
        #print ('different vars')
        return False


def reporting(original_list, sorted_list, name):
    relation_group = {}
    file = 'Reports/Statistics/' + name + '_detail.txt'
    writer = open(file, 'w')
    for i in sorted_list:
        if i[1] not in relation_group.keys():
            relation_group[i[1]] = 0
        relation_group[i[1]] += 1
        if int(i[0]) < 100000:
            writer.write(str(i[0]) + '  : ' + str(i[1]) + '\n')
        else:
            writer.write(str(i[0]) + ' : ' + str(i[1]) + '\n')
    writer.write('\n\nSum: ' + str(np.sum(list(original_list.values())))+'\nMean: ' + str(round(np.mean(list(original_list.values())),5)) + '\nSD: ' + str(round(np.std(list(original_list.values())),5)))
    writer.close()
    return relation_group

def adherence_hist(success_dic1, total_dic1, success_dic2, total_dic2, name1, name2):

    adherence1 = {}
    result1 = {}

    adherence2 = {}
    result2 = {}

    for i in success_dic1.keys():
        if total_dic1[i] == 0:
            continue
        auxAd = str(float(success_dic1[i]) / total_dic1[i])
        j = auxAd.index('.')
        adherence1[i] = float(auxAd[:j + 2])
    for k in adherence1.keys():
        if adherence1[k] not in result1:
            result1[adherence1[k]] = 0
        result1[adherence1[k]] += 1

    for i in success_dic2.keys():
        if total_dic2[i] == 0:
            continue
        auxAd = str(float(success_dic2[i]) / total_dic2[i])
        j = auxAd.index('.')
        adherence2[i] = float(auxAd[:j + 2])

    for k in adherence2.keys():
        if adherence2[k] not in result2:
            result2[adherence2[k]] = 0
        result2[adherence2[k]] += 1

    first_add_data(result1, name1, len(result1), "CV adherence")
    second_add_data(result2, name2, len(result2), "CV adherence")
    chisq(0.99)

    for x in [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]:
        if x not in result1:
            result1[x] = 0

    for k in result1.keys():
        result1[k] = float(result1[k]) / len(adherence1)
        if k not in result2.keys():
            result2[k] = 0

    for k in result2.keys():
        result2[k] = float(result2[k]) / len(adherence2)
        if k not in result1.keys():
            result1[k] = 0

    daux1 = sorted(result1.items(), key=operator.itemgetter(0))
    valores1 = []
    llaves1 = []
    for i in daux1:
        valores1.append(i[1])
        llaves1.append(i[0])

    daux2 = sorted(result2.items(), key=operator.itemgetter(0))
    valores2 = []
    llaves2 = []
    for i in daux2:
        valores2.append(i[1])
        llaves2.append(i[0])

    X = np.arange(max(len(daux1), len(daux2)))
    if len(llaves1) > len(llaves2):
        llaves = llaves1
    else:
        llaves = llaves2


    pl.bar(X + 0.3, valores1, align='center', width=0.4, color = 'green', alpha = 0.5, label = name1)
    pl.bar(X + 0.7, valores2, align='center', width=0.4, color = 'blue', alpha = 0.5, label = name2)
    pl.legend(loc = 'upper left')
    pl.xticks(X, llaves)
    pl.xlabel("Adherence")
    pl.ylabel("Patients")
    ymax = 1
    pl.ylim(0, ymax)
    pl.show()

def statistic_hist(diccionario1, diccionario2,  number1, number2, name1, name2):
    for k in diccionario1:
        if k in diccionario2:
            first_add_data(diccionario1[k], name1, number1, k)
            second_add_data(diccionario2[k], name2, number2, k)
    lista_relaciones = chisq(0.99)
    return lista_relaciones

def hist_sample(dic1, dic2, name1, name2, xlab, ylab):

    for i in dic1:
        if i not in dic2:
            dic2[i] = 0

    for i in dic2:
        if i not in dic1:
            dic1[i] = 0

    daux1 = sorted(dic1.items(), key=operator.itemgetter(0))
    valores1 = []
    llaves1 = []
    for i in daux1:
        valores1.append(i[1])
        llaves1.append(i[0])

    daux2 = sorted(dic2.items(), key=operator.itemgetter(0))
    valores2 = []
    llaves2 = []
    for i in daux2:
        valores2.append(i[1])
        llaves2.append(i[0])

    X = np.arange(max(len(daux1), len(daux2)))
    if len(llaves1) > len(llaves2):
        llaves = llaves1
    else:
        llaves = llaves2

    pl.bar(X - 0.15, valores1, align='center', width=0.3, color = 'green', alpha = 0.5, label = name1)
    pl.bar(X + 0.15, valores2, align = 'center', width=0.3, color = 'blue', alpha = 0.5, label = name2)
    pl.legend(loc = 'upper left')
    pl.xticks(X, llaves)
    pl.xlabel(xlab)
    pl.ylabel(ylab)
    ymax = 1
    pl.ylim(0, ymax)
    pl.show()

def alignment(lista):
    offset = int(lista[0])
    for i in range(len(lista)):
        lista[i] = int(lista[i]) - offset

def graph(patient_dic, titlelabel):
    for patient in patient_dic.keys():
        alignment(patient_dic[patient][0])
        pl.plot(patient_dic[patient][0], patient_dic[patient][1])
    pl.plot([0,21],[7,7], 'r--', linewidth=2.0)
    ticks  = [0, 7, 14, 21]
    pl.xlabel('month')
    pl.xticks(ticks)
    pl.ylabel('compensation')
    pl.title('Sample: ' + str(titlelabel))
    pl.show()


def detailed_adherence_test(clusters):
    writer = open('Reports/Explicit Derivation/Adherence/Detailed/role_detailed_p_values.csv', 'w')
    writer2 = open('Reports/Explicit Derivation/Adherence/Detailed/role_detailed_cluster_frequency.csv', 'w')
    writer.write('MEDICO->MEDICO\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0

    ##MEDICO -> MEDICO
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            print(reader.readline().split(';')[2])
            s1 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[2]) > 0):
                    s1.append(float(lista[1])/float(lista[2]))
                
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[2]) > 0):
                    s2.append(float(lista[1])/float(lista[2]))

            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1))+';'+str(len(s1)))
        writer2.write('\n')
        if i == len(clusters) - 2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2))+';'+str(len(s2)))
            writer2.write('\n')


        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n')
    
    
    
    writer.write('MEDICO->ENFERMERA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0

    ##MEDICO -> ENFERMERA
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            print(reader.readline().split(';')[4])
            s1 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[4]) > 0):
                    s1.append(float(lista[3])/float(lista[4]))

            reader.close()
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[4]) > 0):
                    s2.append(float(lista[3])/float(lista[4]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1))+';'+str(len(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2))+';'+str(len(s2)))
            writer2.write('\n')

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n') 


    writer.write('MEDICO->NUTRICIONISTA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    
    ##MEDICO -> NUTRICIONISTA
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            s = reader.readline().split(';')
            #print(s)
            #print(s[6])
            s1 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[6]) > 0):
                    s1.append(float(lista[5])/float(lista[6]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            s = reader.readline().split(';')
            print(s[6])
            s2 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[6]) > 0):
                    s2.append(float(lista[5])/float(lista[6]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')

        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1))+';'+str(len(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2))+';'+str(len(s2)))
            writer2.write('\n')        

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n') 


    ##ENFERMERA -> MEDICO
    writer.write('ENFERMERA->MEDICO\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            s = reader.readline().split(';')
            #print(s)
            #print(s[6])
            s1 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[8]) > 0):
                    s1.append(float(lista[7])/float(lista[8]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            s = reader.readline().split(';')
            print(s[8])
            s2 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[8]) > 0):
                    s2.append(float(lista[7])/float(lista[8]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1))+';'+str(len(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2))+';'+str(len(s2)))
            writer2.write('\n')

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n')

    

    ##ENFERMERA -> ENFERMERA
    writer.write('ENFERMERA->ENFERMERA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            s = reader.readline().split(';')
            #print(s)
            #print(s[6])
            s1 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[10]) > 0):
                    s1.append(float(lista[9])/float(lista[10]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            s = reader.readline().split(';')
            print(s[10])
            s2 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[10]) > 0):
                    s2.append(float(lista[9])/float(lista[10]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1))+';'+str(len(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2))+';'+str(len(s2)))
            writer2.write('\n')

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n')

    ##ENFERMERA -> NUTRICIONISTA
    writer.write('ENFERMERA->NUTRICIONISTA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            s = reader.readline().split(';')
            #print(s)
            #print(s[6])
            s1 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[12]) > 0):
                    s1.append(float(lista[11])/float(lista[12]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            s = reader.readline().split(';')
            print(s[12])
            s2 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[12]) > 0):
                    s2.append(float(lista[11])/float(lista[12]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1))+';'+str(len(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2))+';'+str(len(s2)))
            writer2.write('\n')

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n')

    ##NUTRICIONISTA -> MEDICO
    writer.write('NUTRICIONISTA->MEDICO\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            s = reader.readline().split(';')
            #print(s)
            #print(s[6])
            s1 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[14]) > 0):
                    s1.append(float(lista[13])/float(lista[14]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            s = reader.readline().split(';')
            print(s[14])
            s2 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[14]) > 0):
                    s2.append(float(lista[13])/float(lista[14]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1))+';'+str(len(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2))+';'+str(len(s2)))
            writer2.write('\n')

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n')


    ##NUTRICIONISTA -> ENFERMERA
    writer.write('NUTRICIONISTA->ENFERMERA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            s = reader.readline().split(';')
            #print(s)
            #print(s[6])
            s1 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[16]) > 0):
                    s1.append(float(lista[15])/float(lista[16]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            s = reader.readline().split(';')
            print(s[16])
            s2 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[16]) > 0):
                    s2.append(float(lista[15])/float(lista[16]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1))+';'+str(len(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2))+';'+str(len(s2)))
            writer2.write('\n')

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n')

     
    ##NUTRICIONISTA -> NUTRICIONISTA
    writer.write('NUTRICIONISTA->NUTRICIONISTA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            s = reader.readline().split(';')
            #print(s)
            #print(s[6])
            s1 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[18]) > 0):
                    s1.append(float(lista[17])/float(lista[18]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            s = reader.readline().split(';')
            print(s[18])
            s2 = []
            for line in reader:
                lista = line.split(';')
                if (float(lista[18]) > 0):
                    s2.append(float(lista[17])/float(lista[18]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1))+';'+str(len(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2))+';'+str(len(s2)))
            writer2.write('\n')

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n')

    writer2.close()
    writer.close()

def adherence_test(clusters):
    writer = open('Reports/Explicit Derivation/Adherence/Global/role_p_values.csv', 'w')
    writer2 = open('Reports/Explicit Derivation/Adherence/Global/role_cluster_frequency.csv', 'w')
    writer.write('Adherence\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/Nuevos Clusters/PA R ' + clusters[i] + '.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                if int(lista[2]) > 0:
                    s1.append(int(lista[1])/int(lista[2]))
                else:
                    s1.append(0)
            reader.close()

            reader = open('Reports/Explicit Derivation/Nuevos Clusters/PA R ' + clusters[j] + '.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                if int(lista[2]) > 0:
                    s2.append(int(lista[1])/int(lista[2]))
                else:
                    s2.append(0)
            reader.close()
            print (clusters[i] + ' V/S ' + clusters[j])
            writer.write(t_test(s1, s2, 0.95))
            if j < len(clusters) - 1:
                writer.write(';')
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2)))
            writer2.write('\n')
        writer.write('\n')
        index_list += 1

    writer2.close()
    writer.close()

#mode: 0 for all patients, 1 only for those with the referral
def normalized_explicit_test(clusters, mode):
    writer = open('Reports/Explicit Derivation/Derivation/Normalized/derivation_p_values.csv', 'w')
    writer2 = open('Reports/Explicit Derivation/Derivation/Normalized/derivation_cluster_frequency.csv', 'w')

    headers = [0, 'MEDICO->MEDICO\n;', 'MEDICO->ENFERMERA\n;', 'MEDICO->NUTRICIONISTA\n;', 'ENFERMERA->MEDICO\n;', 'ENFERMERA->ENFERMERA\n;', 'ENFERMERA->NUTRICIONISTA\n;', 'NUTRICIONISTA->MEDICO\n;', 'NUTRICIONISTA->ENFERMERA\n;', 'NUTRICIONISTA->NUTRICIONISTA\n;']
    for head in range(1, 10):
        writer.write(headers[head])
        for i in range(len(clusters)):
            writer.write(clusters[i])
            if i < len(clusters) - 1:
                writer.write(';')
        writer.write('\n')
        index_list = 1
        wrote_list = 0

        for i in range(len(clusters)-1):
            writer.write(clusters[i] + ';' + ';'*index_list)
            for j in range(i+1, len(clusters)):
                reader = open('Reports/Explicit Derivation/Norm derivation R '+clusters[i]+'.csv', 'r')
                print(reader.readline().split(';')[head])
                s1 = []
                for line in reader:
                    lista = line.split(';')
                    if mode == 1:
                        if float(lista[head]) > 0.0:
                            s1.append(float(lista[head]))
                    else:
                        s1.append(float(lista[head]))
                reader.close()

                reader = open('Reports/Explicit Derivation/Norm derivation R '+clusters[j]+'.csv', 'r')
                reader.readline()
                s2 = []
                for line in reader:
                    lista = line.split(';')
                    if mode == 1:
                        if float(lista[head]) > 0.0:
                            s2.append(float(lista[head]))
                    else:
                        s2.append(float(lista[head]))
                reader.close()
                if (np.mean(s1) > 0 or np.mean(s2) > 0):
                    print (clusters[i] + ' V/S ' + clusters[j])
                    writer.write(t_test(s1, s2, 0.95))
                else:
                    writer.write('N/A')
                if j < len(clusters) - 1:
                    writer.write(';')
            
            writer2.write(clusters[i] + ';')
            writer2.write(str(np.mean(s1)))
            writer2.write('\n')
            if i == len(clusters) - 2:
                writer2.write(clusters[j] + ';')
                writer2.write(str(np.mean(s2)))
                writer2.write('\n')


            writer.write('\n')
            index_list += 1
        writer.write('\n')
        writer2.write('\n')
    writer.close()
    writer2.close()


if __name__ == "__main__":
    
    #clusters = ['[7-9]', '>9', 'empeora', 'estable', 'mejora', 'Medio_inestable', 'Muy_inestable']
    clusters = ['Delegador', 'Deleg. reasig.', 'Subcon. simple', 'Subcon. multiple', 'Subcon. coord.', "Grupo2", "Grupo Int2"]
    
    #indepence_test("AdherenciaCTCV_label.csv", 0.99)
    adherence_test(clusters)
    #detailed_adherence_test(clusters)
    #normalized_explicit_test(clusters, 1)

    '''
    for i in range(len(clusters)-1):
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PA R ' + clusters[i] + '.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[1])/int(lista[2]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PA R ' + clusters[j] + '.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[1])/int(lista[2]))
            reader.close()
            print (clusters[i] + ' V/S ' + clusters[j])
            t_test(s1, s2, 0.95)
                
    

    #print('\n\n')
    #print('====================')
    #s1 = [6.9, 7.6, 7.3, 7.6, 7.8, 7.2, 8, 5.5, 5.8, 7.3, 8.2, 6.9, 6.8, 5.7, 8.6]
    #s2 = [6.4, 6.7, 5.4, 8.2, 5.3, 6.6, 5.8, 5.7, 6.2, 7.1, 7.0, 6.9, 5.6, 4.2, 6.8]
    #t_test(s1, s2, 0.99)

    
    
    ###IMPLICIT REFERRALS
    ##MEDICO -> MEDICO
    for i in range(len(clusters)-1):
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[1]))
            reader.close()

            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[1]))
            reader.close()
            print (clusters[i] + ' V/S ' + clusters[j])
            t_test(s1, s2, 0.99)
    
    


    ##MEDICO -> ENFERMERA
    for i in range(len(clusters)-1):
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[2]))
            reader.close()
            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[2]))
            reader.close()
            print (clusters[i] + ' V/S ' + clusters[j])
            t_test(s1, s2, 0.99)
            reader.close()

    '''
    '''
    ##MEDICO -> NUTRICIONISTA
    for i in range(len(clusters)-1):
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[3]))
            reader.close()

            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[3]))
            reader.close()
            print (clusters[i] + ' V/S ' + clusters[j])
            t_test(s1, s2, 0.99)

    '''

    '''
    ##ENFERMERA -> MEDICO
    for i in range(len(clusters)-1):
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[4]))
            reader.close()

            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[4]))
            reader.close()
            print (clusters[i] + ' V/S ' + clusters[j])
            t_test(s1, s2, 0.99)

    

    ##ENFERMERA -> ENFERMERA
    for i in range(len(clusters)-1):
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[5]))
            reader.close()

            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                if int(lista[0]) == 113984:
                    continue 
                s2.append(int(lista[5]))
            reader.close()
            print (clusters[i] + ' V/S ' + clusters[j])
            t_test(s1, s2, 0.99)

    
    ##ENFERMERA -> NUTRICIONISTA
    for i in range(len(clusters)-1):
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[6]))
            reader.close()

            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[6]))
            reader.close()
            print (clusters[i] + ' V/S ' + clusters[j])
            t_test(s1, s2, 0.99)

    

    ##NUTRICIONISTA -> MEDICO
    for i in range(len(clusters)-1):
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[7]))
            reader.close()

            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[7]))
            reader.close()
            print (clusters[i] + ' V/S ' + clusters[j])
            t_test(s1, s2, 0.99)

    '''
    '''

    ##NUTRICIONISTA -> ENFERMERA
    for i in range(len(clusters)-1):
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[8]))
            reader.close()

            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[8]))
            reader.close()
            print (clusters[i] + ' V/S ' + clusters[j])
            t_test(s1, s2, 0.99)

    '''

    '''
    ##NUTRICIONISTA -> NUTRICIONISTA
    for i in range(len(clusters)-1):
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[9]))
            reader.close()

            reader = open('Reports/Implicit Derivation/Implicit referrals '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[9]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                t_test(s1, s2, 0.99)



    ##############EXPLICIT REFERRALS####################
    '''

    '''
    for i in range(len(clusters)-1):
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            print(reader.readline().split(';')[10])
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[10]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[10]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                t_test(s1, s2, 0.95)

    '''

    '''
    writer = open('Reports/Explicit Derivation/role_p_values.csv', 'w')
    writer2 = open('Reports/Explicit Derivation/role_cluster_frequency.csv', 'w')

    
    writer.write('MEDICO->MEDICO\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0

    ##MEDICO -> MEDICO
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            print(reader.readline().split(';')[2])
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[2]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[2]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1)))
        writer2.write('\n')
        if i == len(clusters) - 2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2)))
            writer2.write('\n')


        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n')
    
    
    
    writer.write('MEDICO->ENFERMERA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0

    ##MEDICO -> ENFERMERA
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            print(reader.readline().split(';')[4])
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[4]))
            reader.close()
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[4]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2)))
            writer2.write('\n')

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n') 


    writer.write('MEDICO->NUTRICIONISTA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    
    ##MEDICO -> NUTRICIONISTA
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            s = reader.readline().split(';')
            #print(s)
            #print(s[6])
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[6]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            s = reader.readline().split(';')
            print(s[6])
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[6]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')

        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2)))
            writer2.write('\n')        

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n') 


    ##ENFERMERA -> MEDICO
    writer.write('ENFERMERA->MEDICO\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            s = reader.readline().split(';')
            #print(s)
            #print(s[6])
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[8]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            s = reader.readline().split(';')
            print(s[8])
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[8]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2)))
            writer2.write('\n')

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n')

    

    ##ENFERMERA -> ENFERMERA
    writer.write('ENFERMERA->ENFERMERA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            s = reader.readline().split(';')
            #print(s)
            #print(s[6])
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[10]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            s = reader.readline().split(';')
            print(s[10])
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[10]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2)))
            writer2.write('\n')

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n')

    ##ENFERMERA -> NUTRICIONISTA
    writer.write('ENFERMERA->NUTRICIONISTA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            s = reader.readline().split(';')
            #print(s)
            #print(s[6])
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[12]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            s = reader.readline().split(';')
            print(s[12])
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[12]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2)))
            writer2.write('\n')

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n')

    
    

    ##NUTRICIONISTA -> MEDICO
    writer.write('NUTRICIONISTA->MEDICO\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            s = reader.readline().split(';')
            #print(s)
            #print(s[6])
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[14]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            s = reader.readline().split(';')
            print(s[14])
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[14]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2)))
            writer2.write('\n')

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n')


    ##NUTRICIONISTA -> ENFERMERA
    writer.write('NUTRICIONISTA->ENFERMERA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            s = reader.readline().split(';')
            #print(s)
            #print(s[6])
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[16]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            s = reader.readline().split(';')
            print(s[16])
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[16]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2)))
            writer2.write('\n')

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n')

     
    ##NUTRICIONISTA -> NUTRICIONISTA
    writer.write('NUTRICIONISTA->NUTRICIONISTA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Explicit Derivation/PAD R '+clusters[i]+'.csv', 'r')
            s = reader.readline().split(';')
            #print(s)
            #print(s[6])
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[18]))
            reader.close()

            reader = open('Reports/Explicit Derivation/PAD R '+clusters[j]+'.csv', 'r')
            s = reader.readline().split(';')
            print(s[18])
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[18]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        
        writer2.write(clusters[i] + ';')
        writer2.write(str(np.mean(s1)))
        writer2.write('\n')
        if i == len(clusters) -2:
            writer2.write(clusters[j] + ';')
            writer2.write(str(np.mean(s2)))
            writer2.write('\n')

        writer.write('\n')
        index_list += 1
    writer.write('\n')
    writer2.write('\n')

    writer2.close()
    writer.close()
    '''

'''
'''
###IMPLICITA ACTIVIDADES
'''
'''
'''
    writer = open('Reports/Implicit Derivation/activity_p_values.csv', 'w')
    writer.write('ACTIVIDADES GRUPALES\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0

    ##ACTIVIDADES GRUPALES
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/activity_report '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[1]))
            reader.close()

            reader = open('Reports/Implicit Derivation/activity_report '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[1]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        writer.write('\n')
        index_list += 1
    writer.write('\n') 
    

    ##ASISTENTE SOCIAL
    writer.write('ASISTENTE SOCIAL\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/activity_report '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[2]))
            reader.close()

            reader = open('Reports/Implicit Derivation/activity_report '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[2]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        writer.write('\n')
        index_list += 1
    writer.write('\n')

    ##CONSULTA NUTRICIONAL
    writer.write('CONSULTA NUTRICIONAL\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/activity_report '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[5]))
            reader.close()

            reader = open('Reports/Implicit Derivation/activity_report '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[5]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        writer.write('\n')
        index_list += 1
    writer.write('\n')

    ##CONSULTA PSICOLOGICA
    writer.write('CONSULTA PSICOLOGICA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/activity_report '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[8]))
            reader.close()

            reader = open('Reports/Implicit Derivation/activity_report '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[8]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        writer.write('\n')
        index_list += 1
    writer.write('\n')

    ##ENCARGADO DE FAMILIA
    writer.write('ENCARGADO DE FAMILIA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/activity_report '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[12]))
            reader.close()

            reader = open('Reports/Implicit Derivation/activity_report '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[12]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        writer.write('\n')
        index_list += 1
    writer.write('\n')

    ##EVALUACION PIE
    writer.write('EVALUACION PIE DM\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/activity_report '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[13]))
            reader.close()

            reader = open('Reports/Implicit Derivation/activity_report '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[13]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        writer.write('\n')
        index_list += 1
    writer.write('\n')
    
    ##TRATAMIENTO PIE
    writer.write('TRATAMIENTO PIE DIABETICO\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/activity_report '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[18]))
            reader.close()

            reader = open('Reports/Implicit Derivation/activity_report '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[18]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        writer.write('\n')
        index_list += 1
    writer.write('\n')
    
    ##VISITA DOMICILIARIA
    writer.write('VISITA DOMICILIARIA\n;')
    for i in range(len(clusters)):
        writer.write(clusters[i])
        if i < len(clusters) - 1:
            writer.write(';')
    writer.write('\n')
    index_list = 1
    wrote_list = 0
    for i in range(len(clusters)-1):
        writer.write(clusters[i] + ';' + ';'*index_list)
        for j in range(i+1, len(clusters)):
            reader = open('Reports/Implicit Derivation/activity_report '+clusters[i]+'.csv', 'r')
            reader.readline()
            s1 = []
            for line in reader:
                lista = line.split(';')
                s1.append(int(lista[19]))
            reader.close()

            reader = open('Reports/Implicit Derivation/activity_report '+clusters[j]+'.csv', 'r')
            reader.readline()
            s2 = []
            for line in reader:
                lista = line.split(';')
                s2.append(int(lista[19]))
            reader.close()
            if (np.mean(s1) > 0 or np.mean(s2) > 0):
                print (clusters[i] + ' V/S ' + clusters[j])
                writer.write(t_test(s1, s2, 0.95))
            else:
                writer.write('N/A')
            if j < len(clusters) - 1:
                writer.write(';')
        writer.write('\n')
        index_list += 1

    writer.close()


'''

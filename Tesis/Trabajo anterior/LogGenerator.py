__author__ = 'Tania'

from datetime import datetime


def is_in_range(date, daterange):
    d1 = datetime.strptime(date[:10], "%Y/%m/%d")
    for i in range(len(daterange)):
        # dStart = datetime.strptime(daterange[i][0], "%Y-%m-%d")
        # dEnd = datetime.strptime(daterange[i][1], "%Y-%m-%d")
        dStart = daterange[i][0]
        dEnd = daterange[i][1]
        if dStart < d1 < dEnd:
            #print(daterange, i)
            return i
    return -1




def generate_log(filter, pacientes, file, center, decompensation_window_DC):
    filtro = filter
    bigLog = open(file, 'r')
    filteredLog = open('Log/' + filtro + '_' + str(decompensation_window_DC) + 'm_' + center + '.csv', 'w')
    filteredLog.write(bigLog.readline())
    for line in bigLog:
        tags = line.split(';')
        if int(tags[0]) in pacientes.keys():
            x = is_in_range(tags[3], pacientes[int(tags[0])][filtro])
            if x != -1:
                filteredLog.write(str(x) + '_' + line)



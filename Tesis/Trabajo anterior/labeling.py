reader = open('Log/log_final.csv', 'r')
referrals = open('Log/log-detailed.csv', 'r')
writer = open('Log/labeled-log2.csv', 'w')

referrals.readline()
writer.write(reader.readline().strip() + ';tag;cluster\n')

patients = {}
p_in_cluster = {}
for line in referrals:
    info_list = line.strip().split(';')
    patients[info_list[1]] = {}
    p_in_cluster[info_list[1]] = info_list[0]
    for i in range(2, len(info_list)):
        patients[info_list[1]][info_list[i][:3]] = info_list[i][4:]

for line in reader:
    info_list = line.strip().split(';')
    patient_case = info_list[2]
    professional = info_list[5].replace('"', '')
    if info_list[8].replace('"', '') == 'CTCV' and patient_case in patients and patient_case in p_in_cluster:
        if professional in patients[patient_case]:
            writer.write(line.strip() + ';' + patients[patient_case][professional] + ';' + p_in_cluster[patient_case] + '\n')
        else:
            writer.write(line.strip() + ';NO INFO;NO CLUSTER\n')
    else:
        writer.write(line.strip() + ';NO INFO;NO CLUSTER\n')

reader.close()
referrals.close()
writer.close()






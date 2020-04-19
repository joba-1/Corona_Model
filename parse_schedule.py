import numpy.random as npr

def parse_schedule(file_name):
    schedules = {}  ## {age (upper_bound): [[schedule1,schedule2],[p1,p2]]}

    input_file = open('inputs/'+file_name+'.csv','r')
    input_file = input_file.readlines()
    del(input_file[0])

    current_key = 0
    current_sched = 0
    upper_bounds = []
    entries = []

    for line in input_file:
        line = line.split('\t')
        if line[0]:
            if line[0][0].isdigit() or line[0][0]=='i':
                schedules[float(line[0])] = [[{'times':[], 'locs':[]}],[float(line[2])]]
                current_key = float(line[0])
                current_sched = int(line[1])-1
                upper_bounds.append(float(line[0]))
        elif line[1]:
            schedules[current_key][0].append({'times':[], 'locs':[]})
            schedules[current_key][1].append(float(line[2]))
            current_sched = int(line[1])-1

        time = 0
        duration = 0
        entries.append(sum([1 for e in [3,6,9,12,15,18,21] if line[e]]))

        #print(' ',current_key,current_sched,entries)
        
        if line[3]:

            ## monday
            ##print(line[3][0],line[3][0]=='p')
            if line[3][0]=='p':
                if line[4]:
                    duration = npr.randint(int(line[3][1:]),int(line[4]))
                else:   duration = int(line[3][1:])
                #print(' ',duration)
                time = schedules[current_key][0][current_sched]['times'][-entries[-2]]+duration   # -number of days with entry when days are finisched
                #print(' ',time)
            else:
                if line[4]:
                    time = npr.randint(int(line[3]),int(line[4]))
                else:   time = int(line[3])
            schedules[current_key][0][current_sched]['times'].append(time)
            schedules[current_key][0][current_sched]['locs'].append(line[5].strip('\n'))

            ## tuesday
        if line[6]:
            if line[6] in ['mo']:      # ['mo','tu','we','th','fr','sa']:
                time = schedules[current_key][0][current_sched]['times'][-1]+24
            else:
                if line[6][0]=='p':
                    if line[7]:
                        duration = npr.randint(int(line[6][1:]),int(line[7]))
                    else:   duration = int(line[6][1:])
                    time = schedules[current_key][0][current_sched]['times'][-entries[-2]]+duration
                else:
                    if line[7]:
                        time = npr.randint(int(line[6])+24,int(line[7])+24)
                    else:   time = int(line[6])+24
            schedules[current_key][0][current_sched]['times'].append(time)
            schedules[current_key][0][current_sched]['locs'].append(line[8].strip('\n'))

            ## wednesday
        if line[9]:
            if line[9] in ['mo','tu']:      # ['mo','tu','we','th','fr','sa']:
                if line[9]=='mo':
                    time = schedules[current_key][0][current_sched]['times'][-2]+48
                else:
                    time = schedules[current_key][0][current_sched]['times'][-1]+24
            else:
                if line[9][0]=='p':
                    if line[10]:
                        duration = npr.randint(int(line[9][1:]),int(line[10]))
                    else:   duration = int(line[9][1:])
                    time = schedules[current_key][0][current_sched]['times'][-entries[-2]]+duration
                else:
                    if line[10]:
                        time = npr.randint(int(line[9])+48,int(line[10])+48)
                    else:   time = int(line[9])+48
            schedules[current_key][0][current_sched]['times'].append(time)
            schedules[current_key][0][current_sched]['locs'].append(line[11].strip('\n'))

            ## thursday
        if line[12]:
            if line[12] in ['mo','tu','we']:      # ['mo','tu','we','th','fr','sa']:
                if line[12]=='mo':
                    time = schedules[current_key][0][current_sched]['times'][-3]+72
                elif line[12]=='tu':
                    time = schedules[current_key][0][current_sched]['times'][-2]+48
                else:
                    time = schedules[current_key][0][current_sched]['times'][-1]+24
            else:
                if line[12][0]=='p':
                    if line[13]:
                        duration = npr.randint(int(line[12][1:]),int(line[13]))
                    else:   duration = int(line[12][1:])
                    time = schedules[current_key][0][current_sched]['times'][-entries[-2]]+duration
                else:
                    if line[13]:
                        time = npr.randint(int(line[12])+72,int(line[13])+72)
                    else:   time = int(line[12])+72
            schedules[current_key][0][current_sched]['times'].append(time)
            schedules[current_key][0][current_sched]['locs'].append(line[14].strip('\n'))

            ## friday
        if line[15]:
            if line[15] in ['mo','tu','we','th']:      # ['mo','tu','we','th','fr','sa']:
                if line[15]=='mo':
                    time = schedules[current_key][0][current_sched]['times'][-4]+96
                elif line[15]=='tu':
                    time = schedules[current_key][0][current_sched]['times'][-3]+72
                elif line[15]=='we':
                    time = schedules[current_key][0][current_sched]['times'][-2]+48
                else:
                    time = schedules[current_key][0][current_sched]['times'][-1]+24
            else:
                if line[15][0]=='p':
                    if line[16]:
                        duration = npr.randint(int(line[15][1:]),int(line[16]))
                    else:   duration = int(line[15][1:])
                    time = schedules[current_key][0][current_sched]['times'][-entries[-2]]+duration
                else:
                    if line[16]:
                        time = npr.randint(int(line[15])+96,int(line[16])+96)
                    else:   time = int(line[15])+96
            schedules[current_key][0][current_sched]['times'].append(time)
            schedules[current_key][0][current_sched]['locs'].append(line[17].strip('\n'))

            ## saturday
        if line[18]:
            if line[18] in ['mo','tu','we','th','fr']:      # ['mo','tu','we','th','fr','sa']:
                if line[18]=='mo':
                    time = schedules[current_key][0][current_sched]['times'][-5]+120
                elif line[18]=='tu':
                    time = schedules[current_key][0][current_sched]['times'][-4]+96
                elif line[18]=='we':
                    time = schedules[current_key][0][current_sched]['times'][-3]+72
                elif line[18]=='th':
                    time = schedules[current_key][0][current_sched]['times'][-2]+48
                else:
                    time = schedules[current_key][0][current_sched]['times'][-1]+24
            else:
                if line[18][0]=='p':
                    if line[19]:
                        duration = npr.randint(int(line[18][1:]),int(line[19]))
                    else:   duration = int(line[18][1:])
                    time = schedules[current_key][0][current_sched]['times'][-entries[-2]]+duration
                else:
                    if line[19]:
                        time = npr.randint(int(line[18])+120,int(line[19])+120)
                    else:   time = int(line[18])+120
            schedules[current_key][0][current_sched]['times'].append(time)
            schedules[current_key][0][current_sched]['locs'].append(line[20].strip('\n'))

            ## sunday
        if line[21]:
            if line[21] in ['mo','tu','we','th','fr','sa']:      # ['mo','tu','we','th','fr','sa']:
                if line[21]=='mo':
                    time = schedules[current_key][0][current_sched]['times'][-6]+144
                elif line[21]=='tu':
                    time = schedules[current_key][0][current_sched]['times'][-5]+120
                elif line[21]=='we':
                    time = schedules[current_key][0][current_sched]['times'][-4]+96
                elif line[21]=='th':
                    time = schedules[current_key][0][current_sched]['times'][-3]+72
                elif line[21]=='th':
                    time = schedules[current_key][0][current_sched]['times'][-2]+48
                else:
                    time = schedules[current_key][0][current_sched]['times'][-1]+24
            else:
                if line[21][0]=='p':
                    if line[22]:
                        duration = npr.randint(int(line[21][1:]),int(line[22]))
                    else:   duration = int(line[21][1:])
                    time = schedules[current_key][0][current_sched]['times'][-entries[-2]]+duration
                else:
                    if line[22]:
                        time = npr.randint(int(line[21])+144,int(line[22])+144)
                    else:   time = int(line[21])+144
            schedules[current_key][0][current_sched]['times'].append(time)
            schedules[current_key][0][current_sched]['locs'].append(line[23].strip('\n'))

    upper_bounds.sort()
    schedules['upper_bounds']=upper_bounds

    return schedules

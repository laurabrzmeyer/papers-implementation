import pandas as pd
import numpy as np
from datetime import datetime
from ast import literal_eval
import statistics
from collections import Counter

def get_time(data, te, cycle, win):

    tests = list(data['Test'].unique())
    times = []
    for tc in tests:
        execs_portion = data[(data['Cycle']>=(cycle-win))&(data['Cycle']<cycle)&(data['Test']==tc)&(data['Status']=='Passed')] 
        if(len(execs_portion)>=2):
            times.append(statistics.median(list(execs_portion['Duration'])))
        elif(len(execs_portion)==1):
            times.append(list(execs_portion['Duration'])[0])
        else:
            times.append(list(te[te['Test']==tc]['Time'])[0])
    
    return pd.DataFrame({'Test':tests, 'Time':times})

def get_time_execution(data, exec_type, input_path):

    tests = list(data['Test'].unique())
    duration_all = list(data[data['Duration']>0]['Duration'])
    duration_mean = sum(duration_all)/len(duration_all)
    not_have = []

    te = pd.read_csv(input_path+'/TE_'+exec_type+'.csv', sep=';')
        
    time_execution = []
    for tc in tests:
        execs = data[data['Test']==tc]
        execs_passed = execs[execs['Status']=='Passed']
        durations = list(execs_passed[execs_passed['Duration']>0]['Duration'])
        # Get median of executions when PASSED -----------------------------------------------------> MEDIAN FROM PASSED RESULTS IN INPUT
        if(len(durations)>0):
            duration_median = statistics.median(durations)
        # Never PASSED in input data
        else:
            time = list(te[te['Test']==tc]['Time'])
            # PASSED in all data -------------------------------------------------------------------> MEDIAN FROM PASSED RESULTS IN ALL DATA
            if(len(time)>0):
                assert len(time)==1
                duration_median = time[0]
            # Never PASSED -------------------------------------------------------------------------> MEDIAN FROM FAILED RESULTS IN INPUT
            else:
                not_have.append(tc)
                duration_median = statistics.median(list(execs['Duration']))
        time_execution.append(duration_median)

    df = pd.DataFrame({'Test':tests, 'Time':time_execution}) 
    print('>>> Never PASS: ' + str(len(not_have)) + ' tests')

    return df

def getMF(execution, LabelType):

    if(len(execution)>0):
        Si = list(execution[LabelType])[0]
    else:
        Si = -1
                
    # Si passed
    if(Si==0):
        MF = 1
    else:
        #Si failed
        if(Si==1):
            MF = -1
        #Not executed
        else:
            MF = 0
    
    return MF

def getPrioMF(MF, v, j):

    P_tc = 0
    for i in range(0,len(MF)):
        if(i==0):
            w = 0.7
        else:
            if(i==1):
                w = 0.2
            else:
                w = 0.1
        P_tc = P_tc + (MF[i][j]*w)

    return P_tc

def getPrioMF_1(MF, j, win):

    P_tc = 0
    i = 0
    interation = 1
    while(i<=win):
        if(MF[i][j]!=0):
            if(i==0):
                w = 0.7
            else:
                if(i==1):
                    w = 0.2
                else:
                    w = 0.1
            P_tc = P_tc + (MF[i][j]*w)
            i = i + 1
        else:
            if(interation>len(MF)):
                i = win + 1
        interation += 1

    return P_tc

def getPrioMF_2(MF, j, win):

    P_tc = 0
    i = 0
    while(i<=win):
        if(i==0):
            w = 0.7
        else:
            if(i==1):
                w = 0.2
            else:
                w = 0.1
        P_tc = P_tc + (MF[i][j]*w)
        i = i + 1

    return P_tc

def getPrioROCKET(tests, Prio, te):

    df = pd.DataFrame({'Test':tests, 'Prio':Prio})
    df_classes = pd.DataFrame({'Class':sorted(set(Prio))}).reset_index(drop=False)
    Prio_Class = []
    for index, row in df.iterrows():
        Class = row['Prio']
        prio = list(df_classes[df_classes['Class']==Class]['index'])[0] + 1
        Prio_Class.append(prio)
    df['Prio_Class'] = Prio_Class
        
    te_v = te[te['Test'].isin(list(df['Test']))]
    Tmax = max(te_v['Time'])

    Ps = []
    for index, row in df.iterrows():

        tc = row['Test']
        p = row['Prio_Class']
        time = list(te_v[te_v['Test']==tc]['Time'])[0]
        if(time>Tmax):
            t = max(df['Prio_Class'])
            p_new = t + 1
        else:
            p_new = p + (time/Tmax)

        Ps.append(p_new)

    df['Prio_ROCKET'] = Ps

    return df

def get_apfd_verdict(order, present, LabelType):

    list_fails = []
    i = 1
    for tc in order:
        s = list(present[present['Test']==tc][LabelType].unique())
        if(s[0]==1):
            list_fails.append(i)
        i = i + 1
    
    try:
        apfd = 1 - (sum(list_fails)/(len(order)*len(list_fails))) + (1/(2*len(order)))
    except:
        apfd = np.nan
    
    return apfd

def get_bugs(data, LabelType):

    data_fail = data[data[LabelType]==1]
    bugs = list(data_fail['Bugs'].unique())
    bugs_in_data = []

    for bs in bugs:
        list_bugs = bs.replace('[','').replace(']','').replace('\'','').split(', ')
        for b in list_bugs:
            if(b in bugs_in_data):
                pass
            else:
                if(b!=''):
                    bugs_in_data.append(b)

    return bugs_in_data

def get_apfd_issue(order, present, LabelType):

    list_bugs = get_bugs(present, LabelType)
    bugs_already_know = []
    order_bugs = []

    i = 1

    for tc in order:
        s = present[present['Test']==tc]
        assert len(s) == 1
        if(list(s[LabelType])[0]==1):
            b = get_bugs(s, LabelType)
            if(len(b)>0):
                if(len(set(b)-set(bugs_already_know))>0):
                    order_bugs.append(i)
                    bugs_already_know = list(set(bugs_already_know + b))
        i = i + 1

    try:
        apfd = 1 - (sum(order_bugs)/(len(order)*len(order_bugs))) + (1/(2*len(order)))
    except:
        apfd = np.nan

    return apfd

def get_apfd_issue_unique(order, present, LabelType):

    order_bugs = []

    i = 1

    for tc in order:
        s = present[present['Test']==tc]
        b = list(s[LabelType.replace('_Unique', '')])
        assert len(b)==1
        if(b[0]==1):
            order_bugs.append(i)
        i = i + 1

    try:
        apfd = 1 - (sum(order_bugs)/(len(order)*len(order_bugs))) + (1/(2*len(order)))
    except:
        apfd = np.nan

    return apfd

def get_apfd(order, present, LabelType):
    
    if((LabelType=='Verdict')|(LabelType=='Verdict_Ref')):
        apfd = get_apfd_verdict(order, present, LabelType)
    elif((LabelType=='Issue')|(LabelType=='Issue_Ref')):
        apfd = get_apfd_issue(order, present, LabelType)
    elif((LabelType=='Issue_Unique')|(LabelType=='Issue_Ref_Unique')):
        apfd = get_apfd_issue_unique(order, present, LabelType)
    else:
        print('ERROR')

    return apfd

def get_apfd_mean(df):

    versions = list(df['Version'].unique())
    method = list(df['Method'].unique())
    Mean_H = []
    cycles = []

    for v in versions:

        df_v = df[df['Version']==v]
        cycles.append(list(df_v['Cycle'].unique())[0])
        df_v = df_v.dropna(subset=['APFD'])
        apfd_h = list(df_v['APFD'])
        if(len(apfd_h)>0):
            apfd_mean_h = sum(apfd_h)/len(apfd_h)
        else:
            apfd_mean_h = np.nan
        Mean_H.append(apfd_mean_h)
        
    df_mean = pd.DataFrame({'Cycle':cycles, 'Version':versions, 'APFD':Mean_H, 'Method':method*len(versions)})

    return df_mean
        
def check_exo(dfs, col):

    CountsDF = {}
    found = 0
    i = 1
    for df in dfs:
        Counts = {}
        group = df.groupby(col).count().reset_index(drop=False)
        counts_tc = list(group['Test'].unique())
        if((len(counts_tc)==1)&(counts_tc[0]==1)):
            pass
        else:
            for c in counts_tc:
                if(c!=1):
                    Counts[c] = list(group[group['Test']==c][col])
            found += 1
        CountsDF[i] = Counts
        i += 1
        
    if(found>0):
        return [True, CountsDF]
    else:
        return [False, CountsDF]

def check_exo2(dfs, col):

    prios_exo = []
    dict_exo = {}
    df_name = 1
    for df in dfs:
        dict_exo_df = {}
        prios = df[col]
        dict_count = Counter(prios)
        exos = set(dict_count.values())
        if((len(exos)==1)&(list(exos)[0]==1)):
            pass
        else:
            for key in dict_count:
                if(dict_count[key]!=1):
                    prios_exo.append(key)
                    dict_exo_df[dict_count[key]] = key
        dict_exo[df_name] = dict_exo_df
        df_name += 1
        
    if(len(prios_exo)>0):
        return [True, dict_exo]
    else:
        return [False, dict_exo]
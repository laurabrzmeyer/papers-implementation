import pandas as pd
import numpy as np
from datetime import datetime
from ast import literal_eval
import statistics
from collections import Counter

def getMF(execution):

    if(len(execution)>0):
        Si = list(execution['Verdict'])[0]
    else:
        Si = -1
                
    # If passed
    if(Si==0):
        MF = 1
    else:
        #If failed
        if(Si==1):
            MF = -1
        #If not executed
        else:
            MF = 0
    
    return MF

def getPrioMF(MF, j, win, case='1'):

    P_tc = 0
    i = 0
    
    if(case=='1'):
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

    elif(case=='2'):
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

    else:
        assert 0==1, 'Error! Case not available!'

    return P_tc

def getPrioROCKET(data_win, tests, Prio):

    df = pd.DataFrame({'Test':tests, 'Prio':Prio})
    df_classes = pd.DataFrame({'Class':sorted(set(Prio))}).reset_index(drop=False)
    Prio_Class = []
    for index, row in df.iterrows():
        Class = row['Prio']
        prio = list(df_classes[df_classes['Class']==Class]['index'])[0] + 1
        Prio_Class.append(prio)
    df['Prio_Class'] = Prio_Class
        
    Tmax = max(data_win['Duration'])

    Ps = []
    for index, row in df.iterrows():
        tc = row['Test']
        p = row['Prio_Class']
        time = list(data_win[data_win['Test']==tc]['Duration'])[0]
        if(time>Tmax):
            t = max(df['Prio_Class'])
            p_new = t + 1
        else:
            p_new = p + (time/Tmax)

        Ps.append(p_new)

    df['Prio_ROCKET'] = Ps

    return df

def get_bugs(data):

    data_fail = data[data['Verdict']==1]
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

def get_apfd(order, present, LabelType=='Verdict'):

    list_fails = []
    i = 1

    if(LabelType=='Verdict'):
        for tc in order:
            s = list(present[present['Test']==tc][LabelType].unique())
            if(s[0]==1):
                list_fails.append(i)
            i = i + 1
            
    elif(LabelType=='Issue'):
        list_bugs = get_bugs(present)
        bugs_already_know = []
        for tc in order:
            s = present[present['Test']==tc]
            assert len(s) == 1
            if(list(s[LabelType])[0]==1):
                b = get_bugs(s, LabelType)
                if(len(b)>0):
                    if(len(set(b)-set(bugs_already_know))>0):
                        list_fails.append(i)
                        bugs_already_know = list(set(bugs_already_know + b))
            i = i + 1

    else:
        assert 0==1, 'Error! LabelType not available!'

    try:
        apfd = 1 - (sum(list_fails)/(len(order)*len(list_fails))) + (1/(2*len(order)))
    except:
        apfd = np.nan
    
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

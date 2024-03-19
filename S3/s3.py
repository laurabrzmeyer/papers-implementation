import pandas as pd

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

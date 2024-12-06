def get_bugs(data):

    data_fail = data[data['Result']==1]
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

def get_apfd(order, present, Scenario='Verdict'):

    list_fails = []
    i = 1

    if(Scenario=='Verdict'):
        for tc in order:
            s = list(present[present['Test']==tc]['Result'].unique())
            if(s[0]==1):
                list_fails.append(i)
            i = i + 1
            
    elif(Scenario=='Issue'):
        list_bugs = get_bugs(present)
        bugs_already_know = []
        for tc in order:
            s = present[present['Test']==tc]
            assert len(s) == 1
            if(list(s['Result'])[0]==1):
                b = get_bugs(s)
                if(len(b)>0):
                    if(len(set(b)-set(bugs_already_know))>0):
                        list_fails.append(i)
                        bugs_already_know = list(set(bugs_already_know + b))
            i = i + 1

    else:
        assert 0==1, 'Error! {} Scenario not available!'.format(Scenario)

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

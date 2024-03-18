import pandas as pd
import numpy as np
import tools, os, sys, pickle
import seaborn as sns
from ast import literal_eval
from pathlib import Path
from sklearn.utils import shuffle

INTERACTIONS = 30
INPUT_PATH = 'Data/'
OUTPUT_PATH = 'Output_S3/'
DATABASES = ['Database1', 'Database2']

cols_essential = ['Cycle', 'Version', 'Test', 'Status', 'Verdict', 'Duration', 'Bugs']

for directory in DATABASES:

    print(INTERACTIONS, ' experiments for :', directory, '...')

    path = os.path.join(OUTPUT_PATH, directory) 
    Path(path).mkdir(parents=True, exist_ok=True) 

    data_input = pd.read_csv(INPUT_PATH+directory+'.csv', sep=';')[cols_essential]

    byCycle = data_input.groupby('Cycle')
    cycles = list(byCycle.groups.keys())
  
    APFD1, APFD2, Orders_H1, Orders_H2 = ([] for i in range(4))
    EXP, VERSIONS, CYCLES = ([] for i in range(3)]
    WIN = 5

    for exp in range(0,INTERACTIONS):

        for c in cycles:
            
            present = byCycle.get_group(c)
            version_c = list(present['Version'].unique())[0]
                
            byTC = present.groupby('Test')
            tcs = list(byTC.groups.keys())

            if(c>5):

                i_len = c
                j_len = len(tcs)
                MF = [[0 for _ in range(j_len)] for _ in range(i_len)]
                j = 0
                data_win = data_input[(data_input['Cycle']<c)&(data_input['Cycle']>=c-win)]
                Prio = []
              
                for tc in tcs:

                    # ROCKET
                    past_data = data_input[data_input['Cycle']<c]
                    exec_tc = past_data[past_data['Test']==tc]
                    
                    for i in range(0, i_len):
                        execution = exec_tc[exec_tc['Cycle']==(c-(i+1))]
                        MF[i][j] = tools.getMF(execution)
                        
                    P_tc = tools.getPrioMF(MF, j, WIN)
                    Prio.append(P_tc)

                    j = j + 1  
   
                df = tools.getPrioROCKET(data_win, tcs, Prio)
                df = df.sample(frac=1).reset_index(drop=True)
                
                order_h1 = list(df.sort_values('Prio', ascending=True)['Test'])
                apfd_h1 = tools.get_apfd(order_h1, present)
                order_h2 = list(df.sort_values('Prio_ROCKET', ascending=True)['Test'])
                apfd_h2 = tools.get_apfd(order_h2, present)

            else:
                order_h1, order_h2 = ([] for i in range(2))
                apfd_h1, apfd_h2 = [np.nan, np.nan]

            Orders_H1.append(order_h1)
            Orders_H2.append(order_h2)
            APFD1.append(apfd_h1)
            APFD2.append(apfd_h2)
            EXP.append(exp)
            VERSIONS.append(version_c)
            CYCLES.append(c)

    df1 = pd.DataFrame({'Experiment':EXP, 'Cycle':CYCLES, 'Version':VERSIONS, 'APFD':APFD1, 'Order':Orders_H1})
    df1['Method'] = 'ROCKET without Time'
    df1_mean = tools.get_apfd_mean(df1)

    df2 = pd.DataFrame({'Experiment':EXP, 'Cycle':CYCLES, 'Version':VERSIONS, 'APFD':APFD2, 'Order':Orders_H2})
    df2['Method'] = 'ROCKET with Time'
    df2_mean = tools.get_apfd_mean(df2)

    df = pd.concat([df1, df2], ignore_index=True)
    df.to_csv(path+'/S3_Graal'+str(INTERACTIONS)+'.csv', sep=';', index=False)

    df_mean = pd.concat([df1_mean, df2_mean], ignore_index=True)
    df_mean.to_csv(path+'/S3_APFD.csv', sep=';', index=False)
    sns.set(rc={'figure.figsize':(10,5)})
    swarm_plot = sns.boxplot(data=df_mean, x="APFD", y="Method")
    fig = swarm_plot.get_figure()
    fig.savefig(path+"/S3_APFD.png") 

    print('Done!')

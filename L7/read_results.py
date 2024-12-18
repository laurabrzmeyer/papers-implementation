import pandas as pd
import glob, os
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import statistics
from pathlib import Path
import warnings
from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

import stats

DATA_DIR = 'L7_Raw_Outputs/'

def map_versions_steps(data, path_input):
    list_nan = len(data)*['NaN']
    data.insert(len(list(data.columns)), "Version", list_nan, True)
    df = pd.read_csv(path_input, sep=';')
    cycles = list(df['Cycle'].unique())
    versions = []
    for c in cycles:
        v = list(df[df['Cycle']==c]['Version'].unique())
        assert len(v)==1
        versions.append(v[0])
        data.loc[data.step == c, 'Version'] = v[0]
    map_cv = pd.DataFrame({'Cycle':cycles, 'Version':versions})
    return map_cv, data

def get_method(data):
    list_nan = len(data)*['NaN']
    data.insert(len(list(data.columns)), "Method", list_nan, True)
    data['rewardfun'] = data['rewardfun'].fillna('NaN')
    agents = list(data['agent'].unique())
    rewards = list(data['rewardfun'].unique())
    for p in agents:
        for r in rewards:
            name_method = p + ' + ' + r
            data.loc[(data.agent == p)&(data.rewardfun == r), 'Method'] = name_method
    return data
 
def get_graal(df_data, ITERATIONS, folder_name):
    retecs = df_data.rename(columns={'iteration':'Experiment', 'step':'Cycle', 'order_schedule':'Order', 'napfd':'APFD'})
    retecs = get_method(retecs)
    df = retecs[['Experiment', 'Cycle', 'Version', 'APFD', 'Order', 'Method']]
    df.to_csv(folder_name+'/L7_Graal'+str(ITERATIONS)+'.csv', sep=';', index=False)

def read_results(ITERATIONS, DATASETS, LabelType, path_input): 
    for dataset in DATASETS:
        output_path = f'{DATA_DIR}/{LabelType}_{dataset}/'
        search_pattern = 'rq_*_stats.p'
        filename = 'rq'
        iteration_results = glob.glob(os.path.join(output_path, search_pattern))
        aggregated_results = os.path.join(output_path, filename)
        df_init = stats.load_stats_dataframe(iteration_results, aggregated_results)
        df_init.loc[(df_init['detected'] + df_init['missed']) == 0, 'napfd'] = np.nan
        map_cv, df_data = map_versions_steps(dataset, df_init, path_input)
        get_graal(df_data, ITERATIONS, output_path)

def compare_rewards(df_init_pure, method_, path_to_save):
    cycles = list(df_init_pure['step'].unique())
    reward = ['tcfail', 'timerank', 'failcount']
    DF = {}
    for i in range(0,len(reward)):
        df_reward = df_init_pure[df_init_pure['rewardfun']==reward[i]]
        df_method = df_reward[df_reward['agent']==method_]
        apfd = []        
        for cycle in cycles:
            exps = df_method[df_method['step']==cycle]
            apfds = list(exps['napfd'])
            apfd.append(np.mean(apfds))
        df = pd.DataFrame({'Cycle':cycles, 'APFD':apfd})
        df.loc[:,'Method'] = reward[i]
        DF[i] = df        
    df_all = pd.concat([DF[0], DF[1], DF[2]], ignore_index=True)
    ax = sns.boxplot(data=df_all, x="APFD", y="Method")
    ax.set(xlabel='APFD', ylabel='Reward')
    plt.savefig(f"{path_to_save}/{method_}_rewards.pdf", format='pdf', bbox_inches="tight")

def compare_methods(df_init_pure, path_to_save):
    df_init_pure['rewardfun'] = df_init_pure['rewardfun'].fillna('NaN')
    methods = ['heur_sort', 'heur_weight', 'heur_random', 'tableau', 'mlpclassifier']
    cycles = list(df_init_pure['step'].unique())
    i = 0
    DF = {}
    for m in methods:            
        df_agent = df_init_pure[df_init_pure['agent']==m]
        rewards = list(df_agent['rewardfun'].unique())        
        for r in rewards:                    
            df_reward = df_agent[df_agent['rewardfun']==r]            
            apfd = []
            method_name = []
            for cycle in cycles:
                exps = df_reward[df_reward['step']==cycle]
                apfds = list(exps['napfd'])
                apfd.append(np.mean(apfds))
                if(isinstance(r,float)):
                    method_name.append(m)
                else:
                    method_name.append(m + ' + ' + r)
            df = pd.DataFrame({'Cycle':cycles, 'APFD':apfd, 'Method':method_name})
            DF[i] = df
            i = i + 1
    df_all = pd.concat([DF[0], DF[1], DF[2], DF[3], DF[4], DF[5], DF[6], DF[7], DF[8]], ignore_index=True)
    df_all.to_csv(path_to_save+'/L7_APFD.csv',sep=';',index=False)
    path_fig = path_to_save + '/Figures'
    Path(path_fig).mkdir(parents=True, exist_ok=True)
    ax = sns.boxplot(data=df_all, x="APFD", y="Method")
    plt.savefig(path_fig+"/Retecs.png")
    plt.savefig(path_fig+"/Retecs.pdf", format='pdf', bbox_inches="tight")
    plt.clf()
    to_considere = {}
    for m in ['tableau', 'mlpclassifier']:
        Comp_APFD = {}
        for r in ['failcount', 'timerank', 'tcfail']:
            Comp_APFD[r] = np.mean(df_all[df_all['Method']== m + ' + ' + r]['APFD'])
        id_to = max(Comp_APFD.values())
        to_considere[m] = list(Comp_APFD.keys())[list(Comp_APFD.values()).index(id_to)]
    return to_considere

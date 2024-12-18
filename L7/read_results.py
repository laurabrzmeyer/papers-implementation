import pandas as pd
import glob
import os
import stats
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import statistics
from pathlib import Path

import warnings
from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
 
root = 'C:/Users/mlbrzezins/Documents/Code/SiLi/L7/L7_Obj1/'
INPUT_PATH = 'C:/Users/mlbrzezins/Documents/Code/Input/RETECS/'
DATA_DIR = root + 'Output_L7/Output_L7_'
FIGURE_DIR = 'Output_L7/Figures'

def compare_rewards(df_init_pure, method_):

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
    #plt.savefig("RESULTS/Figures/"+method_+"_rewards.png")
    #plt.savefig("RESULTS/Figures/"+method_+"_rewards.pdf", format='pdf', bbox_inches="tight")

def compare_methods(df_init_pure, path):

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
    df_all.to_csv(path+'/L7_APFD.csv',sep=';',index=False)

    path_fig = path + '/Figures'
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

def get_order(df, agent, reward):

    df_agent = df[df['agent']==agent]  
    df_reward = df_agent[df_agent['rewardfun']==reward] 

    Scheduled_TCs = []

    for index, row in df_reward.iterrows():     
        a = row['order_schedule']        
        Scheduled_TCs.append(a)

    df_reward.loc[:,'Order_RETECS'] = Scheduled_TCs
    #df_reward['Order_RETECS'] = Scheduled_TCs

    return df_reward

def get_order_RETECS(df_tableau, df_mlp):

    cycles = list(df_tableau['step'].unique())
    Order_tableau = []
    Order_mlp = []
    Versions = []
    for c in cycles:
        dft = df_tableau[df_tableau['step']==c].sort_values(by='napfd', ascending=False).reset_index(drop=True)
        order_tableau = dft['Order_RETECS'][0]
        dfnn = df_mlp[df_mlp['step']==c].sort_values(by='napfd', ascending=False).reset_index(drop=True)
        order_mlp = dfnn['Order_RETECS'][0]
        Order_tableau.append(order_tableau)
        Order_mlp.append(order_mlp)
        v = list(dft['Version'].unique())
        if(len(v)==1):
            Versions.append(v[0])
        else:
            print('Error in get_order_RETECS!')
    
    order_retecs = pd.DataFrame({'Cycle':cycles, 'Version':Versions, 'Order_Tableau':Order_tableau, 'Order_NN':Order_mlp})

    return order_retecs

def map_versions_steps(ecu, data, path_input):

    list_nan = len(data)*['NaN']
    data.insert(len(list(data.columns)), "Version", list_nan, True)
    
    df = pd.read_csv(path_input+'/Input_' + ecu.split('_SEP_')[0] + '_RETECS.csv', sep=';')

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

def get_graal(df_data, folder_name):

    retecs = df_data.rename(columns={'iteration':'Experiment', 'step':'Cycle', 'order_schedule':'Order', 'napfd':'APFD'})
    
    retecs = get_method(retecs)

    df = retecs[['Experiment', 'Cycle', 'Version', 'APFD', 'Order', 'Method']]
    df.to_csv(folder_name+'/L7_Graal'+str(30)+'.csv', sep=';', index=False)

def read_results(DATASETS, LabelType):
        
    for dataset in DATASETS:

        ecu_names = dataset.split('_SEP_')
        output_path = DATA_DIR + LabelType + '_' + ecu_names[-1] + '/' + ecu_names[0] + '/'

        search_pattern = 'rq_*_stats.p'
        filename = 'rq'

        iteration_results = glob.glob(os.path.join(output_path, search_pattern))
        aggregated_results = os.path.join(output_path, filename)
        df_init = stats.load_stats_dataframe(iteration_results, aggregated_results)

        df_init.loc[(df_init['detected'] + df_init['missed']) == 0, 'napfd'] = np.nan

        path_input = 'C:/Users/mlbrzezins/Documents/Code/Input/RETECS/' + dataset.split('_SEP_')[-1]
        map_cv, df_data = map_versions_steps(dataset, df_init, path_input)

        get_graal(df_data, output_path)

        df_data.to_csv(output_path+'/Test.csv', sep=';', index=False)

        to_considere = compare_methods(df_data, output_path)

        order_tableau = get_order(df_data, 'tableau', to_considere['tableau'])
        oreder_mlp = get_order(df_data, 'mlpclassifier', to_considere['mlpclassifier'])

        order_retecs = get_order_RETECS(order_tableau, oreder_mlp)
        order_retecs.to_csv(output_path+'/L7_Order.csv', sep=';', index=False)
    
def plot_comp(dataTypes, LabelType):

    APFD = pd.DataFrame()
    for dt in dataTypes:
        ecu_names = dt.split('_SEP_')
        apfd = pd.read_csv(DATA_DIR + LabelType + '_' + ecu_names[-1] + '/' + ecu_names[0] + '/L7_APFD.csv', sep=';')
        apfd = apfd[~apfd['Method'].isin(['heur_random + NaN', 'heur_sort + NaN', 'heur_weight + NaN'])]
        #typed = ecu_names[-1]
        typed = ecu_names[0]
        if(typed!=''):
            apfd['Type'] = typed
        else:
            apfd['Type'] = 'Original'
        APFD = pd.concat([APFD, apfd], ignore_index=True)

    ax = sns.boxplot(data=APFD, x="APFD", y="Method", hue='Type')
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1,1))
    plt.savefig(DATA_DIR + LabelType + '_' + ecu_names[-1] + "/Comp_Retecs.png", bbox_inches='tight')
    plt.clf()

#DATASETS = ['Auto_IVC_SEP_TE_LastRun', 'Manu_IVC_SEP_TE_LastRun', 'Auto_IVI_SEP_TE_LastRun', 'Manu_IVI_SEP_TE_LastRun']
#plot_comp(DATASETS, 'Issue_Ref')

"""
DeepOrder METHOD
* This script is an adaptation of Aizaz Sharif's DeepOrder_on_Cisco_Dataset.py code 
* Accessed in April 2023
* Available at: https://github.com/T3AS/DeepOrder-ICSME21/blob/main/DeepOrder_on_Cisco_Dataset.py

Implementation by Maria Laura Brzezinski Meyer
Last modification: 08-12-2024

References:
    A. Sharif, D. Marijan, and M. Liaaen, 
    "DeepOrder: Deep Learning for Test Case Prioritization in Continuous Integration Testing,"
    2021 IEEE Int. Conf. on Software Maintenance and Evolution (ICSME), pp. 525–534.
    Available at: https://arxiv.org/abs/2110.07443
"""

import pandas as pd
import numpy as np
from statistics import mean, stdev
import os
import keras.backend as K
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime
import warnings
warnings.simplefilter(action='ignore')
from pathlib import Path
import multiprocessing

from l4 import L4
from functions import *

ITERACTIONS = 30
INPUT_PATH = 'Path/To/Input/'
DATASETS = ['Dataset1', 'Dataset2']
OUTPUT_PATH = 'Path/To/Save/Outputs/'
VARIANTS = ['L4.1', 'L4.2']
PARALLEL_POOL_SIZE = 4  # for 2 datasets and 2 methods
PARALLEL = True
cols_essential = ['Cycle', 'Version', 'Test', 'Result', 'Bugs', 'Duration', 'DurationFeature', 'E1', 'E2', 'E3', 'LastRunFeature', 'DIST', 'CHANGE_IN_STATUS', 'PRIORITY_VALUE']


def run_experiment(data_name, input_path, variant, output_path, cols_essential, ITERACTIONS):

    print(f'Running L4 method ({variant}) for {d} ...')

    ALGO = L4(variant, input_path)
    df = ALGO.INP[cols_essential]

    Orders, cycles_true, versions, EXP = ([] for len_v in range(4))

    for index_for in range(0,ITERACTIONS):

        config = tf.compat.v1.ConfigProto()
        config.gpu_options.allow_growth = True
        session = tf.compat.v1.Session(graph=tf.compat.v1.get_default_graph(), config=config)

        values = pd.DataFrame()
        values['Id'] = range(0, 1)
        values['env'] = data_name

        X = df[['DurationFeature', 'E1','E2','E3', 'LastRunFeature','DIST','CHANGE_IN_STATUS']] # Defining feature variable
        Y = df['PRIORITY_VALUE'] # Defining label variable
        MSE_list = [] # mean square error list
        R2_list=[]  

        # ### Deep Neural Network 
        X_train, X_test, y_train, y_test = split_dataset(X, Y)
        model = Sequential()
        model.add(Dense(10, input_shape=(7,), activation=mish))
        model.add(Dense(20, activation=mish))
        model.add(Dense(15, activation=mish))
        model.add(Dense(1,))
        model.compile(Adam(lr=0.001), loss='mean_squared_error', metrics=[soft_acc])
        information = model.fit(X_train, y_train, validation_data= (X_test, y_test), epochs = 1000, validation_split = 0.2,
                                shuffle = True, verbose = 1)
        y_test_pred = prediction_function(X_train, X_test, model)    
        MSE_list.append(mean_squared_error(y_test, y_test_pred))
        R2_list.append(r2_score(y_test, y_test_pred))       
        outcome = pd.DataFrame({'Actual': y_test, 'Predicted': y_test_pred.flatten()})

        #---------------------#

        values['MSE_list'] = mean(MSE_list)
        print('Average Mean Squared Error: %.6f'% mean(MSE_list))
        if (len(MSE_list)>1):
            print('Standard Deviation of MSE: %.6f'% stdev(MSE_list))

        values['R2_list'] = mean(R2_list)

        print('Average R2 Score: %.6f'% mean(R2_list))
        if (len(R2_list) >1):
            print('Standard Deviation of R2 Score: %.6f'% stdev(R2_list))

        data_scaler = MinMaxScaler()
        # m is number of fault in dataset
        _,m=df['Result'].value_counts()
        n=df.shape[0]
        values['Number of Failed Tests'] = m
        values['Total Test Cases'] = n

        data_scaler = MinMaxScaler()
        XX = data_scaler.fit_transform(df[['DurationFeature', 'E1','E2','E3', 'LastRunFeature','DIST','CHANGE_IN_STATUS']])
        A = model.predict(XX)
        df['CalcPrio'] = A
        final_df = df.sort_values(by=['CalcPrio'], ascending=True)
        final_df['ranking'] = range(1, 1+len(df))

        missing = []
        Last_cycle = int(max(df['Cycle']))
        print (Last_cycle, " will be last cycle")

        for index in range (1,Last_cycle):

            df_temp = df.loc[df['Cycle']==(index)]
            v = list(df_temp['Version'].unique())
            
            if(len(v)==0):
                versions.append('NaN')
            else:
                assert len(v)==1    
                versions.append(v[0])

            if (index<=Last_cycle and index in list(df['Cycle'].unique())):

                cycles_true.append(index)
                EXP.append(index_for)

                if (df_temp.empty):
                    missing.append(index)
                    Orders.append([])
                    continue
                    
                XX = data_scaler.fit_transform(df_temp[['DurationFeature', 'E1','E2','E3', 'LastRunFeature', 'DIST','CHANGE_IN_STATUS']])
                A = model.predict(XX)
                df_temp['CalcPrio'] = A
                df_temp = df_temp.sample(frac=1).reset_index(drop=True)
                final_df_temp = df_temp.sort_values(by=['CalcPrio'], ascending=True)
                order = list(final_df_temp['Test'])
                Orders.append(order)                
                counts = final_df_temp['Result'].value_counts().to_dict()

            else:
                cycles_true.append(index)
                EXP.append(index_for)
                Orders.append([])

    # Saving order
    df_graal = pd.DataFrame({'Experiment':EXP, 'Cycle':cycles_true, 'Version':versions, 'Order':Orders})
    df_graal['Method'] = variant
    df_graal.to_csv(f'{output_path}/L4_Graal{str(ITERACTIONS)}.csv', sep=';', index=False)
                
if __name__ == '__main__':
    
    now = datetime.now()
    print('START:', now)

    experiments = []
    for d in DATASETS:
        data_path = os.path.join(INPUT_PATH, d) 
        out_path = os.path.join(OUTPUT_PATH, d) 
        Path(out_path).mkdir(parents=True, exist_ok=True) 
        for v in VARIANTS:            
            experiments.append(d, data_path, v, out_path, cols_essential, ITERACTIONS)

    if PARALLEL:
      p = multiprocessing.Pool(PARALLEL_POOL_SIZE)
      avg_res = p.starmap(run_experiment, experiments)
    else:
      for i in experiments:
        run_experiment(i[0], i[1], i[2], i[3], i[4], i[5], i[6])

    end = datetime.now()
    print('END:', end)
    print('Time spend:', end-now)
import pandas as pd
import os
from pathlib import Path
import multiprocessing
import time

from Tools.input_data import input_data
from S3.s3 import S3
from S22.s22 import S22
from S26.s26 import S26
from S34.s34 import S34

INTERACTIONS = 30
DATASETS = ['Dataset1', 'Dataset2']
INPUT_PATH = 'Path/To/Input/'
OUTPUT_PATH = 'Path/To/Save/Outputs/'
WIN = {'S3':3, 'S22':5, 'S26':5, 'S34':10}
PARALLEL_POOL_SIZE = 8  # for 2 datasets and 4 methods
PARALLEL = True
METHOD = ['S3', 'S22', 'S26', 'S34']
VARIANTS = {'S3':['S3.1.1', 'S3.1.2', 'S3.2.1', 'S3.2.2'], 'S22':['S22.1', 'S22.2'], 
            'S26':['S26.1.1', 'S26.1.2', 'S26.2.1', 'S26.2.2'], 'S34':['S34.1.1', 'S34.1.2', 'S34.2.1', 'S34.2.2']}


def run_experiment(INTERACTIONS, INPUT_PATH, OUTPUT_PATH, input_file, WIN, method, variants, budget=1.0):
  
    print(f'{INTERACTIONS} experiments for : {directory} using {method} {variants} ...')

    path = os.path.join(OUTPUT_PATH, directory) 
    Path(path).mkdir(parents=True, exist_ok=True) 

    data_input = pd.read_csv(f'{INPUT_PATH}/{input_file}.csv', sep=';', dtype={'Cycle':int, 'Version':str, 'Test':str, 'Result':int})
    INP = input_data(str(input_file), data_input, f'{INPUT_PATH}/{input_file}.csv') 

    OREDERS, SELEC, APFD, NAPFD = ({} for i in range(4))
    for n in variants:
        OREDERS[n] = []
        SELEC[n] = []
        APFD[n] = []
        NAPFD[n] = []

    EXP, VERSIONS, CYCLES = [[] for i in range(3)]

    for exp in range(0,INTERACTIONS):
      
        cycles = INP.cycles
        interaction = 1

        M = {}
        past_data = {}
        for n in variants:
            M[n] = S3(n, INP, WIN)
            past_data[n] = pd.DataFrame()

        for c in cycles:

            version_c = INP.version
            present = INP.present
            tc_availables = INP.tc_availables
            if(budget==1.0):
                bntc = len(present)
            else:
                bntc = round(budget*len(present))

            order, selection = [{} for i in range(2)]
            for n in variants:
                # Change cycle
                if(interaction>1):
                    INP.next_cycle()
                # Get order if WIN cycles have already passed
                if(interaction>WIN):
                    order[n] = M[n].get_prio()
                    selection[n] = order[n][0:bntc]
                    # In case of selection, data of the current cycle for not selected tests will not be available in the next cycle
                    if(budget<1.0):
                        INP.update_past(selection[n])
                    else:
                        assert len(order[n])==len(selection[n])
                else:
                    order[n] = []
                    selection[n] = []
                assert INP.get_current_cycle()==c
                OREDERS[n].append(order[n])
                SELEC[n].append(selection[n])
                
            EXP.append(exp)
            VERSIONS.append(version_c)
            CYCLES.append(c)

            interaction = interaction+1

    concat_df = pd.DataFrame()
    for n in variants:
        df = pd.DataFrame({'Experiment':EXP, 'Cycle':CYCLES, 'Version':VERSIONS, 'Order':OREDERS[n], 'Selection':SELEC[n]})
        df['Method'] = n
        concat_df = pd.concat([concat_df, df], ignore_index=True)

    concat_df.to_csv(f'{path}/{method}_Graal{str(INTERACTIONS)}.csv', sep=';', index=False)
    
    print('{} done for {}!'.format(method, input_file))

if __name__ == '__main__':

    start_time = time.time()
  
    items = []
    for d in DATASETS:
      for m in METHODS:
        items.append((INTERACTIONS, INPUT_PATH, OUTPUT_PATH, d, WIN[m], m, VARIANTS[m]))

    if PARALLEL:
      p = multiprocessing.Pool(PARALLEL_POOL_SIZE)
      avg_res = p.starmap(run_experiment, items)
    else:
      for i in items:
        run_experiment(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7])
    
    time_spent = round((time.time()-start_time)/60, 2)
    print('All experiments done in {} minutes!'.format(time_spent))

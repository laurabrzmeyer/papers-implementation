import pandas as pd
import os
from pathlib import Path
import multiprocessing
import time
from s3 import S3

INTERACTIONS = 30
DATASETS = ['Dataset1', 'Dataset2']
INPUT_PATH = 'Path/To/Input/'
OUTPUT_PATH = 'Path/To/Save/Outputs/'
WIN = 3
PARALLEL_POOL_SIZE = 8
PARALLEL = True
METHOD = 'S3'
VARIANTS = ['S3.1.1', 'S3.1.2', 'S3.2.1', 'S3.2.2']


def run_experiment(INTERACTIONS, INPUT_PATH, OUTPUT_PATH, input_file, WIN, method, variants, budget=1.0):

    print(INTERACTIONS, ' experiments for :', directory, '...')

    path = os.path.join(OUTPUT_PATH, directory) 
    Path(path).mkdir(parents=True, exist_ok=True) 

    data_input = pd.read_csv(f'{INPUT_PATH}/{input_file}.csv', sep=';', dtype={'Cycle':int, 'Version':str, 'Test':str, 'Result':int})

    OREDERS, SELEC, APFD, NAPFD = ({} for i in range(4))
    for n in variants:
        OREDERS[n] = []
        SELEC[n] = []
        APFD[n] = []
        NAPFD[n] = []

    EXP, VERSIONS, CYCLES = [[] for i in range(3)]

    for exp in range(0,INTERACTIONS):

        byCycle = data_input.groupby('Cycle')
        cycles = list(byCycle.groups.keys())

        interaction = 1

        M = {}
        past_data = {}
        for n in variants:
            M[n] = S3(n, WIN, data_input)
            past_data[n] = pd.DataFrame()

        for c in cycles:
            
            present = byCycle.get_group(c)
            tc_availables = list(present['Test'].unique())
            version_c = list(present['Version'].unique())[0]
            if(budget==1.0):
                bntc = len(present)
            else:
                bntc = round(budget*len(present))

            order, selection = [{} for i in range(2)]
            for n in variants:
                # Change cycle
                if(interaction>1):
                    M[n].next_cycle(tc_availables)
                # Get order if WIN cycles have already passed
                if(interaction>WIN):
                    order[n] = M[n].get_prio(past_data[n])
                    selection[n] = order[n][0:bntc]
                    add_to_memory = present[present['Test'].isin(selection[n])]
                    past_data[n] = pd.concat([past_data[n], add_to_memory], ignore_index=True)
                    if(budget==1.0):
                        assert len(order[n])==len(selection[n])
                        assert len(add_to_memory)==len(present)
                else:
                    order[n] = []
                    selection[n] = []
                    past_data[n] = pd.concat([past_data[n], present], ignore_index=True)
                assert M[n].get_current_cycle()==c
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
    
    print('Done for {} {}!'.format(input_file))

if __name__ == '__main__':

    start_time = time.time()
  
    items = []
    for d in DATASETS:
        items.append((INTERACTIONS, INPUT_PATH, OUTPUT_PATH, d, WIN, METHOD, VARIANTS))

    if PARALLEL:
        p = multiprocessing.Pool(PARALLEL_POOL_SIZE)
        avg_res = p.starmap(run_experiment, items)
    else:
        for i in items:
            run_experiment(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7])
    
    time_spent = round((time.time()-start_time)/60, 2)
    print('All experiments done in {} minutes!'.format(time_spent))

"""
COLEMAN METHOD
* This script was created to run COLEMAN experiments

Implementation by Maria Laura Brzezinski Meyer
Last modification: 18-12-2024

References:

    J. A. P. Lima and S. R. Vergilio, 
    "A Multi-Armed Bandit Approach for Test Case Prioritization in Continuous Integration Environments,"
    in IEEE Transactions on Software Engineering, vol. 48, no. 2, pp. 453-465, 1 Feb. 2022, 
    doi: 10.1109/TSE.2020.2992428. 
    Available at: https://ieeexplore.ieee.org/document/9086053

"""

import pandas as pd
import time, math
import multiprocessing
from pathlib import Path

from Tools.input_data import input_data
from l9 import L9

ITERATIONS = 30
DATASETS = ['Dataset1', 'Dataset2']
INPUT_PATH = 'Path/To/Input/'
OUTPUT_PATH = 'Path/To/Output/'
WIN_SIZE = 20
VARIANTS = {'L9.1.1':('eGreedy', 'RBF', 0.3, None), 'L9.1.2':('eGreedy', 'TRR', 0.5, None), 
            'L9.2.1':('UCB', 'RBF', 0.3, None), 'L9.2.2':('UCB', 'TRR', 0.5, None), 
            'L9.3.1':('FRRMAB', 'RBF', 0.3, 1.0), 'L9.3.2':('FRRMAB', 'TRR', 0.3, 1.0)}
PARALLEL = True
PARALLEL_POOL_SIZE = 12  # 2 databases * 2 rewards * 3 policy
BUDGET = 1.0

def run_experiment(data_name, input_path, path_output, variant_name, policy, rwd, C, DF, SW, ITERATIONS, budget):

    SELECTION, ORDER, EXP, CYCLE, VERSION = [[] for i in range(5)]

    data_input = pd.read_csv(f'{input_path}/{data_name}.csv', sep=';', dtype={'Cycle':int, 'Version':str, 'Test':str, 'Result':int})
    INP = input_data(data_name, data_input, f'{input_path}/{data_name}.csv')
    cycles = INP.cycles

    for exp in range(ITERATIONS):

        ALGO = L9(variant_name, data_input, SW, {'Type':policy, 'C':C, 'DF':DF}, rwd)

        for c in cycles:

            order = ALGO.get_prio()

            ORDER.append(order)
            EXP.append(exp)
            CYCLE.append(c)
            VERSION.append(INP.get_current_version())

            if(budget<1.0):
                bg = math.ceil(budget*len(order))
                selection = order[0:bg]
                SELECTION.append(selection)
                INP.update_past(selection)
            else:
                SELECTION.append(order)
                       
            INP.next_cycle()

    df = pd.DataFrame({'Experiment':EXP, 'Cycle':CYCLE, 'Version':VERSION, 'Method':variant_name, 'Order':ORDER, 'Selection':SELECTION})
    df['Dataset'] = data_name
    df['Method'] = variant_name
    df.to_csv(f'{path_output}/{variant_name}_Graal30.csv', sep=';', index=False)

if __name__ == '__main__':

    start_time = time.time()
  
    items = []
    for d in DATASETS:
        for v in VARIANTS.keys():
            variant = VARIANTS[v]
            path_output = f'{OUTPUT_PATH}/{d}/'
            Path(path_output).mkdir(parents=True, exist_ok=True)
            items.append(d, INPUT_PATH, path_output, v, variant[0], variant[1], variant[2], variant[3], WIN_SIZE, ITERATIONS, BUDGET)

    if PARALLEL:
      p = multiprocessing.Pool(PARALLEL_POOL_SIZE)
      avg_res = p.starmap(run_experiment, items)
    else:
      for i in items:
        run_experiment(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8])
    
    time_spent = round((time.time()-start_time)/60, 2)
    print('All experiments done in {} minutes!'.format(time_spent))


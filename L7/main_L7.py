"""
RETECS METHOD
* This script was adapted from Helge Spieker's run_experiment_common.py code 
* Accessed in March 2023
* Available at: https://bitbucket.org/HelgeS/retecs/src/master/run_experiment_common.py

Implementation by Maria Laura Brzezinski Meyer
Last modification: 18-12-2024

References:
    H. Spieker, A. Gotlieb, D. Marijan, and M. Mossige, 
    "Reinforcement learning for automatic test case prioritization and selection in continuous integration," 
    26th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2017), Santa Barbara, CA, USA, 2017, pp. 12-22, 
    doi: 10.1145/3092703.3092709.
    Available at: https://dl.acm.org/doi/10.1145/3092703.3092709

"""

import multiprocessing
from pathlib import Path

import agents, rewards, scenarios, l7
from read_results import read_results

ITERATIONS = 30
DATASETS = ['Dataset1', 'Dataset2']
INPUT_PATH = 'Path/To/Input/'
OUTPUT_PATH = 'Path/To/Output/'
PARALLEL = True
PARALLEL_POOL_SIZE = 5
SCENARIOS_TYPES = ['Verdict', 'Issue']
env_names = {
    'dataset1': 'Dataset 1',
    'dataset2': 'Dataset 2'
}

CI_CYCLES = 1000
DATA_DIR = 'L7_Raw_Outputs/'

method_names = {
    'mlpclassifier': 'Network',
    'tableau': 'Tableau',
    'heur_random': 'Random',
    'heur_sort': 'Sorting',
    'heur_weight': 'Weighting'
}

reward_names = {
    'failcount': 'Failure Count Reward',
    'tcfail': 'Test Case Failure Reward',
    'timerank': 'Time-ranked Reward'
}

reward_funs = {
    'failcount': rewards.failcount,
    'timerank': rewards.timerank,
    'tcfail': rewards.tcfail
}

def run_experiments(exp_fun, datasets, ScenarioType, parallel):
    if parallel:
        p = multiprocessing.Pool(PARALLEL_POOL_SIZE)
        items = []
        for i in range(ITERATIONS):
            items.append((i, datasets, ScenarioType))
        avg_res = p.starmap(exp_fun, items)
    else:
        avg_res = [exp_fun(i, datasets, ScenarioType) for i in range(ITERATIONS)]

def exp_run_industrial_datasets(iteration, datasets, ScenarioType):
    ags = [
        lambda: (agents.TableauAgent(histlen=l7.DEFAULT_HISTORY_LENGTH, learning_rate=l7.DEFAULT_LEARNING_RATE, state_size=l7.DEFAULT_STATE_SIZE, action_size=l7.DEFAULT_NO_ACTIONS, epsilon=l7.DEFAULT_EPSILON),
                 l7.preprocess_discrete, reward_funs.timerank),
        lambda: (agents.NetworkAgent(histlen=l7.DEFAULT_HISTORY_LENGTH, state_size=l7.DEFAULT_STATE_SIZE, action_size=1, hidden_size=l7.DEFAULT_NO_HIDDEN_NODES), 
                 l7.preprocess_continuous, rewards.tcfail)
    ]

    for i, get_agent in enumerate(ags):
        for sc in datasets:
            for (reward_name, reward_fun) in reward_funs.items():

                agent, preprocessor, _ = get_agent()
                file_appendix = 'rq_%s_%s_%s_%d' % (agent.name, sc, reward_name, iteration)

                scenario = scenarios.IndustrialDatasetScenarioProvider(f'{INPUT_PATH}/{sc}.csv', scenarioType=ScenarioType)
                
                raw_output_path = f'{DATA_DIR}/{ScenarioType}_{sc}/'
                Path(output_path).mkdir(parents=True, exist_ok=True)

                rl_learning = l7.PrioLearning(agent=agent,
                                                  scenario_provider=scenario,
                                                  reward_function=reward_fun,
                                                  preprocess_function=preprocessor,
                                                  file_prefix=file_appendix,
                                                  dump_interval=100,
                                                  validation_interval=0,
                                                  output_dir=raw_output_path)

                res = rl_learning.train(no_scenarios=CI_CYCLES,
                                        print_log=False,
                                        plot_graphs=False,
                                        save_graphs=False,
                                        collect_comparison=(i == 0))
                
if __name__ == '__main__':

    for st in SCENARIOS_TYPES:
        run_experiments(exp_run_industrial_datasets, DATASETS, st, PARALLEL)
        for d in DATASETS:
            read_results(ITERATIONS, d, st, INPUT_PATH, OUTPUT_PATH)

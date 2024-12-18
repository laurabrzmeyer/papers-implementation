"""
RL METHOD
* This script was adapted from Helge Spieker's run_experiment_common.py code 
* Accessed in March 2023
* Available at: https://bitbucket.org/HelgeS/retecs/src/master/run_experiment_common.py

Implementation by Maria Laura Brzezinski Meyer
Last modification: 06-12-2024

References:

    H. Spieker, A. Gotlieb, D. Marijan, and M. Mossige, 
    "Reinforcement learning for automatic test case prioritization and selection in continuous integration," 
    26th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2017), Santa Barbara, CA, USA, 2017, pp. 12-22, 
    doi: 10.1145/3092703.3092709.
    Available at: https://dl.acm.org/doi/10.1145/3092703.3092709

    T. Shi, L. Xiao, and K. Wu,  
    "Reinforcement Learning Based Test Case Prioritization for Enhancing the Security of Software,"
    2020 IEEE 7th Int. Conf. on Data Science and Advanced Analytics (DSAA), Sydney, NSW, Australia, 2020, pp. 663-672,   
    doi: 10.1109/DSAA49011.2020.00076.
    Available at: https://ieeexplore.ieee.org/document/9260075

"""

import sys, multiprocessing
from pathlib import Path
from L7 import agents, scenarios, l7
from L8 import rewards

sys.path.insert(0, 'papers-implementation/L7')

ITERATIONS = 30
DATASETS = ['Dataset1', 'Dataset2']
INPUT_PATH = 'Path/To/Input//'
OUTPUT_PATH = 'Path/To/Output/'
PARALLEL = True
PARALLEL_POOL_SIZE = 5
SCENARIOS_TYPES = ['Verdict', 'Issue']
REWARDS = ['rhe_whole_four', 'rhe_whole_all', 'rhe_part_four', 'rhe_part_all', 'the_whole_four', 'the_part_four']
env_names = {
    'dataset1': 'Dataset 1',
    'dataset2': 'Dataset 2'
}

CI_CYCLES = 1000

method_names = {
    'mlpclassifier': 'Network',
    'tableau': 'Tableau',
    'heur_random': 'Random',
    'heur_sort': 'Sorting',
    'heur_weight': 'Weighting'
}

reward_names = {
    'rhe_whole_all': 'RHE whole all',
    'rhe_whole_four': 'RHE whole four',
    'rhe_part_all': 'RHE part all',
    'rhe_part_four': 'RHE part four',
    'the_whole_four': 'THE whole four',
    'the_part_four': 'THE part four'
}

reward_funs = {
    'rhe_whole_all': rewards.Reward('rhe_whole_all'),
    'rhe_whole_four': rewards.Reward('rhe_whole_four'),
    'rhe_part_all': rewards.Reward('rhe_part_all'),
    'rhe_part_four': rewards.Reward('rhe_part_four'),
    'the_whole_four': rewards.Reward('the_whole_four'),
    'the_part_four': rewards.Reward('the_part_four')
}

def run_experiments(exp_fun, dataset, ScenarioType, reward_names, N_INT, parallel):
    if parallel:
        p = multiprocessing.Pool(PARALLEL_POOL_SIZE)
        items = []
        for i in range(N_INT):
            items.append((i, dataset, ScenarioType, reward_names))
        avg_res = p.starmap(exp_fun, items)
    else:
        avg_res = [exp_fun(i, dataset, ScenarioType, reward_names) for i in range(N_INT)]

def exp_run_industrial_datasets(iteration, datasets, ScenarioType, reward_names):
    ags = [
        lambda: (agents.TableauAgent(histlen=l7.DEFAULT_HISTORY_LENGTH, learning_rate=l7.DEFAULT_LEARNING_RATE, state_size=l7.DEFAULT_STATE_SIZE, action_size=l7.DEFAULT_NO_ACTIONS, epsilon=l7.DEFAULT_EPSILON),
                 l7.preprocess_discrete, reward_funs.timerank),
        lambda: (agents.NetworkAgent(histlen=l7.DEFAULT_HISTORY_LENGTH, state_size=l7.DEFAULT_STATE_SIZE, action_size=1, hidden_size=l7.DEFAULT_NO_HIDDEN_NODES), 
                 l7.preprocess_continuous, rewards.tcfail)
    ]

    for i, get_agent in enumerate(ags):
        for sc in datasets:
            for r in reward_names:

                reward_fun = reward_funs[r]
                agent, preprocessor, _ = get_agent()
                file_appendix = 'rq_%s_%s_%s_%d' % (agent.name, sc, r, iteration)

                scenario = scenarios.IndustrialDatasetScenarioProvider(f'{INPUT_PATH}/{sc}.csv', scenarioType=ScenarioType)

                output_path = f'{OUTPUT_PATH}/{sc}_{ScenarioType}/'
                Path(output_path).mkdir(parents=True, exist_ok=True)

                rl_learning = l7.PrioLearning(agent=agent,
                                                scenario_provider=scenario,
                                                reward_function=reward_fun,
                                                preprocess_function=preprocessor,
                                                file_prefix=file_appendix,
                                                dump_interval=100,
                                                validation_interval=0,
                                                output_dir=output_path)

                res = rl_learning.train(no_scenarios=CI_CYCLES,
                                            print_log=False,
                                            plot_graphs=False,
                                            save_graphs=False,
                                            collect_comparison=False)
                
if __name__ == '__main__':

    for sc in SCENARIOS_TYPES:
        for d in DATASETS:
            run_experiments(exp_run_industrial_datasets, d, sc, REWARDS, ITERATIONS, PARALLEL)

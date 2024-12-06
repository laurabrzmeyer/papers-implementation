import multiprocessing
from pathlib import Path
import agents, reward, scenarios, l7

ITERATIONS = 30
CI_CYCLES = 1000

INPUT_PATH = 'Path/To/Input//'
OUTPUT_PATH = 'Path/To/Output/'
PARALLEL = True
PARALLEL_POOL_SIZE = 5
RUN_EXPERIMENT = True
DATASETS = ['Dataset1', 'Dataset2']
SCENARIOS_TYPES = ['Verdict', 'Issue']

cols_essential = ['ID', 'Cycle', 'Version', 'Test', 'Result', 'Bugs', 'TE', 'CalcPrio', 'LastRun', 'LR']

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
    'failcount': reward.failcount,
    'timerank': reward.timerank,
    'tcfail': reward.tcfail
}

env_names = {
    'dataset1': 'Dataset 1',
    'iofrol': 'Dataset 2'
}

def run_experiments(exp_fun, datasets, ScenarioType, cols_essential, parallel=PARALLEL):
    if parallel:
        p = multiprocessing.Pool(PARALLEL_POOL_SIZE)
        items = []
        for i in range(ITERATIONS):
            items.append((i, datasets, ScenarioType, cols_essential))
        avg_res = p.starmap(exp_fun, items)
    else:
        avg_res = [exp_fun(i, datasets, ScenarioType, cols_essential) for i in range(ITERATIONS)]

def exp_run_industrial_datasets(iteration, datasets, ScenarioType, cols_essential):
    ags = [
        lambda: (agents.TableauAgent(histlen=l7.DEFAULT_HISTORY_LENGTH, learning_rate=l7.DEFAULT_LEARNING_RATE, state_size=l7.DEFAULT_STATE_SIZE, action_size=l7.DEFAULT_NO_ACTIONS, epsilon=l7.DEFAULT_EPSILON), 
                 l7.preprocess_discrete, l7.timerank),
        lambda: (agents.NetworkAgent(histlen=l7.DEFAULT_HISTORY_LENGTH, state_size=l7.DEFAULT_STATE_SIZE, action_size=1, hidden_size=l7.DEFAULT_NO_HIDDEN_NODES), 
                 l7.preprocess_continuous, l7.tcfail)
    ]

    for i, get_agent in enumerate(ags):
        for sc in datasets:
            for (reward_name, reward_fun) in reward_funs.items():

                agent, preprocessor, _ = get_agent()
                data_name = sc.split('_SEP_')[0]
                data_folder = INPUT_PATH + sc.split('_SEP_')[-1]
                file_appendix = 'rq_%s_%s_%s_%d' % (agent.name, data_name, reward_name, iteration)

                scenario = scenarios.IndustrialDatasetScenarioProvider(f'{INPUT_PATH}/{data_name}.csv', scenarioType=ScenarioType, cols=cols_essential)

                output_path = f'{OUTPUT_PATH}/{sc}_{ScenarioType}/'
                Path(output_path).mkdir(parents=True, exist_ok=True)

                rl_learning = l7.PrioLearning(agent=agent,
                                              scenario_provider=scenario,
                                              reward_function=reward_fun,
                                              preprocess_function=preprocessor,
                                              file_prefix=file_appendix,
                                              dump_interval=100,
                                              validation_interval=0,
                                              output_dir=output_path, 
                                              scenarioType=ScenarioType)

                res = rl_learning.train(no_scenarios=CI_CYCLES,
                                        print_log=False,
                                        plot_graphs=False,
                                        save_graphs=False,
                                        collect_comparison=(i == 0))
                
if __name__ == '__main__':

    for sc in SCENARIOS_TYPES:
        
        if RUN_EXPERIMENT:
            run_experiments(exp_run_industrial_datasets, DATASETS, sc, cols_essential, parallel=True)

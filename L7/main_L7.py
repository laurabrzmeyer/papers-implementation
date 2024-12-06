import multiprocessing
from pathlib import Path
import agents, reward, scenarios, retecs

ITERATIONS = 30
CI_CYCLES = 1000

INPUT_PATH = 'Path/To/Input//'
OUTPUT_PATH = 'Path/To/Output/'
PARALLEL = True
PARALLEL_POOL_SIZE = 5
RUN_EXPERIMENT = True
DATASETS = ['Dataset1', 'Dataset2']
SCENARIOS_TYPES = ['Verdict', 'Issue']

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

def run_experiments(exp_fun, datasets, ScenarioType, parallel=PARALLEL):
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
        lambda: (
            agents.TableauAgent(histlen=retecs.DEFAULT_HISTORY_LENGTH, learning_rate=retecs.DEFAULT_LEARNING_RATE, state_size=retecs.DEFAULT_STATE_SIZE, action_size=retecs.DEFAULT_NO_ACTIONS, epsilon=retecs.DEFAULT_EPSILON),
            retecs.preprocess_discrete, reward.timerank),
        lambda: (agents.NetworkAgent(histlen=retecs.DEFAULT_HISTORY_LENGTH, state_size=retecs.DEFAULT_STATE_SIZE, action_size=1, hidden_size=retecs.DEFAULT_NO_HIDDEN_NODES), 
                 retecs.preprocess_continuous, reward.tcfail)
    ]

    for i, get_agent in enumerate(ags):
        for sc in datasets:
            for (reward_name, reward_fun) in reward_funs.items():

                agent, preprocessor, _ = get_agent()
                file_appendix = 'rq_%s_%s_%s_%d' % (agent.name, sc, reward_name, iteration)

                scenario = scenarios.IndustrialDatasetScenarioProvider(f'{INPUT_PATH}/{sc}.csv', scenarioType=ScenarioType)

                output_path = f'{OUTPUT_PATH}/{sc}_{ScenarioType}/'
                Path(output_path).mkdir(parents=True, exist_ok=True)

                rl_learning = retecs.PrioLearning(agent=agent,
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
                                        collect_comparison=(i == 0))
                
if __name__ == '__main__':

    for sc in SCENARIOS_TYPES:
        if RUN_EXPERIMENT:
            run_experiments(exp_run_industrial_datasets, DATASETS, sc, parallel=True)

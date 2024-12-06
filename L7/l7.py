"""
RETECS METHOD
* This script was adapted from Helge Spieker's retecs.py code 
* Accessed in 2022
* Available at: https://bitbucket.org/HelgeS/retecs/src/master/retecs.py

Implementation by Maria Laura Brzezinski Meyer
Last modification: 06-12-2024

References:
    H. Spieker, A. Gotlieb, D. Marijan, and M. Mossige, 
    "Reinforcement learning for automatic test case prioritization and selection in continuous integration," 
    26th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2017), Santa Barbara, CA, USA, 2017, pp. 12-22, 
    doi: 10.1145/3092703.3092709.
    Availble at: https://dl.acm.org/doi/10.1145/3092703.3092709

"""

import agents
import datetime, time
import os.path
import numpy as np
import pickle

DEFAULT_NO_SCENARIOS = 1000
DEFAULT_NO_ACTIONS = 100
DEFAULT_HISTORY_LENGTH = 4
DEFAULT_STATE_SIZE = DEFAULT_HISTORY_LENGTH + 1
DEFAULT_LEARNING_RATE = 0.05
DEFAULT_EPSILON = 0.2
DEFAULT_DUMP_INTERVAL = 100
DEFAULT_VALIDATION_INTERVAL = 100
DEFAULT_PRINT_LOG = False
DEFAULT_PLOT_GRAPHS = False
DEFAULT_NO_HIDDEN_NODES = 12
DEFAULT_TODAY = datetime.datetime.today()

def preprocess_discrete(state, scenario_metadata, histlen):
    if scenario_metadata['maxDuration'] > scenario_metadata['minDuration']:
        duration = (scenario_metadata['maxDuration'] - state['Duration']) / (
            scenario_metadata['maxDuration'] - scenario_metadata['minDuration'])
    else:
        duration = 0

    if duration > 0.66:
        duration_group = 2
    elif duration > 0.33:
        duration_group = 1
    else:
        duration_group = 0

    if scenario_metadata['maxExecTime'] > scenario_metadata['minExecTime']:
        time_since = (scenario_metadata['maxExecTime'] - state['LastRun']).total_seconds() / (
            scenario_metadata['maxExecTime'] - scenario_metadata['minExecTime']).total_seconds()
    else:
        time_since = 0

    if time_since > 0.66:
        time_group = 2
    elif time_since > 0.33:
        time_group = 1
    else:
        time_group = 0

    history = [1 if res else 0 for res in state['LR'][0:histlen]]

    if len(history) < histlen:
        history.extend([1] * (histlen - len(history)))

    row = [
        duration_group,
        time_group
    ]
    row.extend(history)

    return tuple(row)


def process_scenario(agent, sc, preprocess):
    scenario_metadata = sc.get_ta_metadata()

    if agent.single_testcases:
        for row in sc.testcases():
            # Build input vector: preprocess the observation
            x = preprocess(row, scenario_metadata, agent.histlen)
            action = agent.get_action(x)
            row['CalcPrio'] = action  # Store prioritization
    else:
        states = [preprocess(row, scenario_metadata, agent.histlen) for row in sc.testcases()]
        actions = agent.get_all_actions(states)

        for (tc_idx, action) in enumerate(actions):
            sc.set_testcase_prio(action, tc_idx)

    # Submit prioritized file for evaluation
    # step the environment and get new measurements
    return sc.submit()


class PrioLearning(object):
    def __init__(self, agent, scenario_provider, file_prefix, reward_function, output_dir, preprocess_function,
                 dump_interval=DEFAULT_DUMP_INTERVAL, validation_interval=DEFAULT_VALIDATION_INTERVAL):
        self.agent = agent
        self.scenario_provider = scenario_provider
        self.reward_function = reward_function
        self.preprocess_function = preprocess_function
        self.replay_memory = agents.ExperienceReplay()
        self.validation_res = []

        self.dump_interval = dump_interval
        self.validation_interval = validation_interval

        self.today = DEFAULT_TODAY

        self.file_prefix = file_prefix
        self.val_file = os.path.join(output_dir, '%s_val' % file_prefix)
        self.stats_file = os.path.join(output_dir, '%s_stats' % file_prefix)
        self.agent_file = os.path.join(output_dir, '%s_agent' % file_prefix)

    def run_validation(self, scenario_count):
        val_res = self.validation()

        for (key, res) in val_res.items():
            res = {
                'scenario': key,
                'step': scenario_count,
                'detected': res[0],
                'missed': res[1],
                'ttf': res[2],
                'napfd': res[3],
                'recall': res[4],
                'avg_precision': res[5],
                'order_schedule':res[6]
                # res[4] are the detection ranks
            }

            self.validation_res.append(res)

    def validation(self):
        self.agent.train_mode = False
        val_scenarios = self.scenario_provider.get_validation()
        keys = [sc.name for sc in val_scenarios]
        results = [self.process_scenario(sc)[0] for sc in val_scenarios]
        self.agent.train_mode = True
        return dict(zip(keys, results))

    def process_scenario(self, sc):
        result = process_scenario(self.agent, sc, self.preprocess_function)
        reward = self.reward_function(result, sc)
        self.agent.reward(reward)
        return result, reward

    def replay_experience(self, batch_size):
        batch = self.replay_memory.get_batch(batch_size)

        for sc in batch:
            (result, reward) = self.process_scenario(sc)
            print('Replay Experience: %s / %.2f' % (result, np.mean(reward)))

    def train(self, no_scenarios, print_log, plot_graphs, save_graphs, collect_comparison=False):
        stats = {
            'scenarios': [],
            'rewards': [],
            'durations': [],
            'detected': [],
            'missed': [],
            'ttf': [],
            'napfd': [],
            'recall': [],
            'avg_precision': [],
            'result': [],
            'step': [],
            'scheduled_tests': [],
            'order_schedule':[],
            #'scheduled_tests2': self.scenario_provider.scheduled_testcases,
            'env': self.scenario_provider.name,
            'agent': self.agent.name,
            'action_size': self.agent.action_size,
            'history_length': self.agent.histlen,
            'rewardfun': self.reward_function.__name__,
            'sched_time': self.scenario_provider.avail_time_ratio,
            'hidden_size': 'x'.join(str(x) for x in self.agent.hidden_size) if hasattr(self.agent, 'hidden_size') else 0
        }

        if collect_comparison:
            cmp_agents = {
                'heur_sort': agents.HeuristicSortAgent(self.agent.histlen),
                'heur_weight': agents.HeuristicWeightAgent(self.agent.histlen),
                'heur_random': agents.RandomAgent(self.agent.histlen)
            }

            stats['comparison'] = {}

            for key in cmp_agents.keys():
                stats['comparison'][key] = {
                    'detected': [],
                    'missed': [],
                    'ttf': [],
                    'napfd': [],
                    'recall': [],
                    'avg_precision': [],
                    'durations': [],
                    'order_schedule':[]
                }

        sum_actions = 0
        sum_scenarios = 0
        sum_detected = 0
        sum_missed = 0
        sum_reward = 0

        for (i, sc) in enumerate(self.scenario_provider, start=1):
            if i > no_scenarios:
                break

            start = time.time()

            if print_log:
                print('ep %d:\tscenario %s\t' % (sum_scenarios + 1, sc.name), end='')

            (result, reward) = self.process_scenario(sc)

            end = time.time()

            # Statistics
            sum_detected += result[0]
            sum_missed += result[1]
            sum_reward += np.mean(reward)
            sum_actions += 1
            sum_scenarios += 1
            duration = end - start

            stats['scenarios'].append(sc.name)
            stats['rewards'].append(np.mean(reward))
            stats['durations'].append(duration)
            stats['detected'].append(result[0])
            stats['missed'].append(result[1])
            stats['ttf'].append(result[2])
            stats['napfd'].append(result[3])
            stats['recall'].append(result[4])
            stats['avg_precision'].append(result[5])
            stats['result'].append(result)
            stats['step'].append(sum_scenarios)
            stats['scheduled_tests'].append(sc.scheduled_testcases)
            stats['order_schedule'].append(result[6])

            if print_log:
                print(' finished, reward: %.2f,\trunning mean: %.4f,\tduration: %.1f,\tresult: %s' %
                      (np.mean(reward), sum_reward / sum_scenarios, duration, result))

            if collect_comparison:
                for key in stats['comparison'].keys():
                    start = time.time()
                    cmp_res = process_scenario(cmp_agents[key], sc, preprocess_discrete)
                    end = time.time()
                    stats['comparison'][key]['detected'].append(cmp_res[0])
                    stats['comparison'][key]['missed'].append(cmp_res[1])
                    stats['comparison'][key]['ttf'].append(cmp_res[2])
                    stats['comparison'][key]['napfd'].append(cmp_res[3])
                    stats['comparison'][key]['recall'].append(cmp_res[4])
                    stats['comparison'][key]['avg_precision'].append(cmp_res[5])
                    stats['comparison'][key]['order_schedule'].append(cmp_res[6])
                    stats['comparison'][key]['durations'].append(end - start)

            # Data Dumping
            if self.dump_interval > 0 and sum_scenarios % self.dump_interval == 0:
                pickle.dump(stats, open(self.stats_file + '.p', 'wb'))

            if self.validation_interval > 0 and (sum_scenarios == 1 or sum_scenarios % self.validation_interval == 0):
                if print_log:
                    print('ep %d:\tRun test... ' % sum_scenarios, end='')

                self.run_validation(sum_scenarios)
                pickle.dump(self.validation_res, open(self.val_file + '.p', 'wb'))

                if print_log:
                    print('done')

        if self.dump_interval > 0:
            self.agent.save(self.agent_file)
            pickle.dump(stats, open(self.stats_file + '.p', 'wb'))

        return np.mean(stats['napfd'])
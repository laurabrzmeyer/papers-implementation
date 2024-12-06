"""
RETECS METHOD
* This script was adapted from Helge Spieker's scenarios.py code 
* Accessed in 2022
* Available at: https://bitbucket.org/HelgeS/retecs/src/master/scenarios.py

Implementation by Maria Laura Brzezinski Meyer
Last modification: 06-12-2024

References:
    H. Spieker, A. Gotlieb, D. Marijan, and M. Mossige, 
    "Reinforcement learning for automatic test case prioritization and selection in continuous integration," 
    26th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2017), Santa Barbara, CA, USA, 2017, pp. 12-22, 
    doi: 10.1145/3092703.3092709.
    Availble at: https://dl.acm.org/doi/10.1145/3092703.3092709

"""

import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import os, random, copy, pickle 
import tools

budget_ntc = {'Auto_IVI': 24, 'Auto_IVC': 25, 'Manu_IVI': 31, 'Manu_IVC': 45}
budget_time = {'Auto_IVI': 15358754, 'Auto_IVC': 15807876, 'Manu_IVI': 11016603, 'Manu_IVC': 926716}


def inhomogeneous_poisson(l, rej_threshold, default=0, size=1):
    values = np.random.poisson(lam=l, size=1)
    rnd_throws = np.random.uniform(size=values.shape)
    values[rnd_throws < rej_threshold] = default
    return values


def generate_testcase(id, last_run, bugs, duration_limits=[180, 1200], history_length=0, history_fail_prob=0.05):
    tc = {
        'ID': id,
        'Duration': random.randint(duration_limits[0], duration_limits[1]),
        'CalcPrio': 0,
        'LastRun': last_run,
        'LR': [1 if random.random() < history_fail_prob else 0 for _ in range(history_length)],
        'Bugs': bugs
    }
    return tc


def generate_solution(tc, basic_failure_chance, prev_failure_influence):
    failure_chance = basic_failure_chance + sum(tc['LR'][0:3]) * prev_failure_influence
    return 1 if random.random() < failure_chance else 0


class VirtualScenario(object):
    def __init__(self, available_time, testcases=[], solutions={}, name_suffix='vrt', schedule_date=datetime.today(), scenarioType='Verdict'):
        self.available_time = available_time
        self.gen_testcases = testcases
        self.solutions = solutions
        self.no_testcases = len(testcases)
        self.name = name_suffix.split('_SPLIT_')[0]
        self.ecu = name_suffix.split('_SPLIT_')[-1]
        self.scheduled_testcases = []
        self.schedule_date = schedule_date
        self.ScenarioType = scenarioType

    def testcases(self):
        return iter(self.gen_testcases)

    def submit(self):
        # Sort tc by Prio ASC (for backwards scheduling), break ties randomly
        sorted_tc = sorted(self.gen_testcases, key=lambda x: (x['CalcPrio'], random.random()))

        if(self.ScenarioType=='Verdict'):
            rank = tools.rank_verdict(sorted_tc, self.available_time, self.solutions, self.scheduled_testcases, ASC=False)
        elif(self.ScenarioType=='Issue'):
            rank = tools.rank_bugs(sorted_tc, self.available_time, self.solutions, self.scheduled_testcases, ASC=False)
        else:
            print('Error in LabelType!')
        
        detection_ranks = rank[0]
        undetected_failures = rank[1]
        order = rank[2]
        self.scheduled_testcases = rank[3]
        detected_failures = rank[4]
        unscheduled_tests = rank[5]
        total_failure_count = rank[6]

        sorted_tc = sorted(self.gen_testcases, key=lambda x: (x['CalcPrio'], random.random()))
        rank_sel, unscheduled_ranks = tools.get_rank_selection(sorted_tc, self.available_time)
        
        assert len(rank_sel)+len(unscheduled_ranks)==len(order)

        if total_failure_count > 0:
            ttf = detection_ranks[0] if detection_ranks else 0

            if undetected_failures > 0:
                p = (detected_failures / total_failure_count)
            else:
                p = 1

            napfd = p - sum(detection_ranks) / (total_failure_count * self.no_testcases) + p / (2 * self.no_testcases)
            recall = detected_failures / total_failure_count
            avg_precision = 123
        else:
            ttf = 0
            napfd = np.nan
            recall = 1
            avg_precision = 1

        return [detected_failures, undetected_failures, ttf, napfd, recall, avg_precision, order, detection_ranks, rank_sel]

    def get_ta_metadata(self):
        execTimes, durations = zip(*[(tc['LastRun'], tc['Duration']) for tc in self.testcases()])

        metadata = {
            'availAgents': 1,
            'totalTime': self.available_time,
            'minExecTime': min(execTimes),
            'maxExecTime': max(execTimes),
            'scheduleDate': self.schedule_date,
            'minDuration': min(durations),
            'maxDuration': max(durations)
        }

        return metadata

    def set_testcase_prio(self, prio, tcid=-1):
        self.gen_testcases[tcid]['CalcPrio'] = prio

    def reduce_to_schedule(self):
        """ Creates a new scenario consisting of all scheduled test cases and their outcomes (for replaying) """
        scheduled_time = sum([tc['Duration'] for tc in self.scheduled_testcases])
        total_time = sum([tc['Duration'] for tc in self.testcases()])
        available_time = self.available_time * scheduled_time / total_time
        solutions = {tc['ID']: self.solutions[tc['ID']] for tc in self.scheduled_testcases}
        return VirtualScenario(available_time, self.scheduled_testcases, solutions, self.name, self.schedule_date)

    def clean(self):
        for tc in self.testcases():
            self.set_testcase_prio(0, tc['ID'] - 1)

        self.scheduled_testcases = []


class RandomScenario(VirtualScenario):
    """ On-the-fly random scenario generator for schedules with only one test agent and without schedule optimization"""

    def __init__(self, schedule_ratio=None, no_testcases=None, history_length=3, init_testcases=False,
                 name_suffix='rnd'):
        super(RandomScenario, self).__init__(available_time=random.randint(14400, 28800), name_suffix=name_suffix)
        self.tc_duration_limit = [180, 1200]
        self.must_run_prob = 0.2
        self.basic_failure_chance = 0.03
        self.prev_failure_influence = 0.5
        self.history_length = history_length

        if no_testcases is None:
            time_to_schedule = self.available_time / schedule_ratio
            self.no_testcases = int(time_to_schedule / np.mean(self.tc_duration_limit))
            self.name = '1_%.1f_%s' % (schedule_ratio, name_suffix)
        else:
            self.no_testcases = no_testcases
            self.name = '1_%d_%s' % (no_testcases, name_suffix)

        self.gen_testcases = []
        self.scheduled_testcases = []
        self.solutions = {}

        if init_testcases:
            list(self.testcases())

    def testcases(self):
        if len(self.gen_testcases) < self.no_testcases:
            for i in range(len(self.gen_testcases), self.no_testcases):
                yield self.generate_testcase()
        else:
            for i in range(self.no_testcases):
                yield self.gen_testcases[i]

    def generate_testcase(self):
        last_run = self.schedule_date - timedelta(days=random.randint(1, 5))

        tc = generate_testcase(id=len(self.gen_testcases) + 1, duration_limits=self.tc_duration_limit,
                               last_run=last_run, history_length=self.history_length)

        self.gen_testcases.append(tc)

        sol = self.generate_solution(tc)
        self.solutions[tc['ID']] = sol
        return tc

    def generate_solution(self, tc):
        return generate_solution(tc, self.basic_failure_chance, self.prev_failure_influence)

    def clean(self):
        for tc in self.testcases():
            self.set_testcase_prio(0, tc['ID'] - 1)

        self.scheduled_testcases = []


class RandomScenarioProvider(object):
    def __init__(self, scenario_class=RandomScenario):
        #self.schedule_ratios = [0.3, 0.5, 0.7, 0.9]
        self.schedule_ratios = [1.0]
        #self.schedule_ratios = [0.4]
        self.validation = []
        self.validation_length = 64
        self.scenario_class = scenario_class
        self.name = 'random'

    def get(self, name_suffix='rnd', init_testcases=False):
        schedule_ratio = random.choice(self.schedule_ratios)
        return self.scenario_class(schedule_ratio=schedule_ratio, init_testcases=init_testcases,
                                   name_suffix=name_suffix)

    def get_validation(self):
        if not self.validation:
            if os.path.exists('%s_validation.p' % type(self).__name__):
                self.validation = pickle.load(open('%s_validation.p' % type(self).__name__, 'rb'))
            else:
                self.validation = [self.get(name_suffix='rnd%d' % i) for i in range(self.validation_length)]
                pickle.dump(self.validation, open('%s_validation.p' % type(self).__name__, 'wb'), 2)

        return copy.deepcopy(self.validation)

    # Generator functions
    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        sc = self.get()

        if sc is None:
            raise StopIteration()

        return sc

class IndustrialDatasetScenarioProvider(RandomScenarioProvider):
    """
    Scenario provider to process CSV files for experimental evaluation of RETECS.

    Required columns are `self.tc_fieldnames` plus ['LabelType', 'Cycle']
    """
    def __init__(self, tcfile, scenarioType, sched_time_ratio=1.0):
        super(IndustrialDatasetScenarioProvider, self).__init__()

        self.basename = os.path.splitext(os.path.basename(tcfile))[0]
        self.name = self.basename
        self.ScenarioType = scenarioType
        self.ecu = self.basename.replace('Input_','').replace('_RETECS','')
        
        temp_tcdf = pd.read_csv(tcfile, sep=';', parse_dates=['LastRun'], dtype={'Duration':float}).fillna('NaN')
        self.tcdf['LR'] = self.tcdf['LR'].apply(json.loads)
        self.solutions = dict(zip(self.tcdf['ID'].tolist(), self.tcdf['Result'].tolist()))

        self.cycle = 0
        self.maxtime = min(self.tcdf.LastRun)
        self.max_cycles = max(self.tcdf.Cycle)
        self.scenario = None
        self.avail_time_ratio = sched_time_ratio
        self.tc_fieldnames = ['ID', 'Test', 'Duration', 'CalcPrio', 'LastRun', 'LR', 'Bugs']

    def get(self, name_suffix=None):
        self.cycle += 1

        if self.cycle > self.max_cycles:
            self.scenario = None
            return None

        cycledf = self.tcdf.loc[self.tcdf.Cycle == self.cycle]

        seltc = cycledf[self.tc_fieldnames].to_dict(orient='records')
        #seltc = self.tcdf[self.tc_fieldnames].to_dict(orient='record')

        if name_suffix is None:
            name_suffix = (self.maxtime + timedelta(days=1)).isoformat()
        #seltc["Duration"] = pd.to_numeric(seltc["Duration"])
        #print(seltc)
        req_time = sum([tc['Duration'] for tc in seltc])
        total_time = req_time * self.avail_time_ratio

        selsol = dict(zip(cycledf['ID'].tolist(), cycledf['Result'].tolist()))

        self.scenario = VirtualScenario(testcases=seltc, solutions=selsol, name_suffix=name_suffix+'_SPLIT_'+self.ecu,
                                        available_time=total_time, schedule_date=self.maxtime + timedelta(days=1), Label=self.LabelType)
        self.maxtime = seltc[-1]['LastRun']

        return self.scenario

    def get_validation(self):
        """ Validation data sets are not supported for this provider """
        return []

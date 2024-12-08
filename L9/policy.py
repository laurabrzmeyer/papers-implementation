"""
COLEMAN METHOD
* This script is an adaptation of Jackson A. P. Lima's coleman4hcs code 
* Accessed in December 2022
* Available at: https://github.com/jacksonpradolima/coleman4hcs

Implementation by Maria Laura Brzezinski Meyer
Last modification: 06-12-2024

References:
    J. A. P. Lima and S. R. Vergilio, 
    "A Multi-Armed Bandit Approach for Test Case Prioritization in Continuous Integration Environments,"
    in IEEE Transactions on Software Engineering, vol. 48, no. 2, pp. 453-465, 1 Feb. 2022, 
    doi: 10.1109/TSE.2020.2992428. 
    Available at: https://ieeexplore.ieee.org/document/9086053
    
"""

import random
import pandas as pd
import numpy as np

class EpsilonGreedy():
    
    def __init__(self, epsilon):
        self.epsilon = epsilon

    def choose(self, tcs, memory):
        avail = memory[memory['Test'].isin(tcs)].sort_values(by='Q', ascending=False).reset_index(drop=True)
        # How much are been selected by "best" value
        qnt_actions = sum([1 for _ in range(len(avail)) if np.random.random() > self.epsilon])
        actions = []
        # Get from top the "n" best values
        if qnt_actions > 0:
            actions = avail.head(qnt_actions)['Test'].tolist()
            temp_actions = avail[~avail.Test.isin(actions)]
        else:
            temp_actions = avail.copy()
        if(len(temp_actions)>0):
            t_actions = temp_actions['Test'].tolist()
            random.shuffle(t_actions)
            actions.extend(t_actions)
        return actions
    
    def credit_assignment(self, prio, rwd, memory):
        weights = np.arange(0.000000000001, 1.0, (1. / len(prio)))[::-1]
        i = 0
        AA, VE, T, Q = [[] for i in range(4)]
        for tc in prio:
            old_memory = memory[memory['Test']==tc]
            aa = list(old_memory['ActionsAttempt'])[0] + weights[i]
            ve = list(old_memory['ValueEstimated'])[0] + rwd[tc]
            t = list(old_memory['T'])[0] + 1
            AA.append(aa)
            VE.append(ve)
            T.append(t)
            Q.append((ve/aa))
            i = i + 1   
        return pd.DataFrame({'Test':prio, 'ActionsAttempt':AA, 'ValueEstimated':VE, 'Q':Q, 'T':T})
    
    def reset(self):
        pass
    
class UCB():
    
    def __init__(self, C):
        self.C = C

    def choose(self, tcs, memory):
        avail = memory[memory['Test'].isin(tcs)].sort_values(by='Q', ascending=False).reset_index(drop=True)
        return list(avail['Test'])
    
    def credit_assignment(self, prio, rwd, memory):
        weights = np.arange(0.000000000001, 1.0, (1. / len(prio)))[::-1]
        i = 0
        AA, VE, T, Q = [[] for i in range(4)]
        for tc in prio:
            old_memory = memory[memory['Test']==tc]
            aa = list(old_memory['ActionsAttempt'])[0] + weights[i]
            ve = list(old_memory['ValueEstimated'])[0] + rwd[tc]
            t = list(old_memory['T'])[0] + 1
            AA.append(aa)
            VE.append(ve)
            T.append(t)
            Q.append((ve/aa))
            i = i + 1
        exploration = np.sqrt((2 * np.log(sum(AA)))/AA)
        exploration[np.isnan(exploration)] = 0
        Q = Q + self.C * exploration
        return pd.DataFrame({'Test':prio, 'ActionsAttempt':AA, 'ValueEstimated':VE, 'Q':Q, 'T':T})
    
    def reset(self):
        pass

class FRRMAB():
    
    def __init__(self, C, decay_factor):
        self.C = C
        self.decayed_factor = decay_factor

    def choose(self, tcs, sum_memory):
        tcs_not_in_memory = list(set(tcs)-set(sum_memory.memory['Test']))
        for tc in tcs_not_in_memory:
            sum_memory.memory = pd.concat([sum_memory.memory, pd.DataFrame([[tc, 0, 0, 0, 0]], columns=sum_memory.memory_columns)], ignore_index=True)
        avail = sum_memory.memory[sum_memory.memory['Test'].isin(tcs)].sort_values(by='Q', ascending=False).reset_index(drop=True)
        return list(avail['Test'])
    
    def observe(self, momentary_memory, prio, rwd):
        # Update Momentary Memory
        weights = np.arange(0.000000000001, 1.0, (1. / len(prio)))[::-1]
        AA =  {prio[i]: weights[i] for i in range(len(prio))}
        momentary_memory.memory["ActionsAttempt"] = momentary_memory.memory["Test"].apply(lambda x: AA.get(x))
        momentary_memory.memory["ValueEstimates"] = momentary_memory.memory["Test"].apply(lambda x: rwd.get(x))
        
    def credit_assignment(self, momentary_memory, cumulative_memory, sum_memory):

        cumulative_memory.update_memory(momentary_memory)

        sum_memory.memory = cumulative_memory.memory.groupby(['Test'], as_index=False).agg({'ActionsAttempt': 'sum', 'ValueEstimates': 'sum', 'T': 'count'})
        sum_memory.memory = sum_memory.memory.sort_values(by='ValueEstimates', ascending=False)
        reward_arm = np.array(sum_memory.memory['ValueEstimates'].values.tolist())
        ranking = np.array(list(range(1, len(reward_arm) + 1)))

        # Compute decay values
        decay_values = np.power(self.decayed_factor, ranking) * reward_arm
        # Compute FRR
        if(sum(decay_values)>0):
            frr = decay_values / sum(decay_values)
        else:
            frr = 0.0

        # Compute Q
        # T column contains the count of usage for each "arm"
        selected_times = np.array(sum_memory.memory['T'].values.tolist())
        exploration = np.sqrt((2 * np.log(sum(selected_times))) / selected_times)
        exploration[np.isnan(exploration)] = 0
        sum_memory.memory['Q'] = frr + self.C * exploration
    
    def reset(self):
        self.history = pd.DataFrame(columns=['Test', 'ActionsAttempt', 'ValueEstimated', 'T'])

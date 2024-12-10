"""
RETECS METHOD
* This script was adapted from Helge Spieker's rewards.py code 
* Accessed in March 2023
* Available at: https://bitbucket.org/HelgeS/retecs/src/master/rewards.py

Implementation by Maria Laura Brzezinski Meyer
Last modification: 06-12-2024

References:
    H. Spieker, A. Gotlieb, D. Marijan, and M. Mossige, 
    "Reinforcement learning for automatic test case prioritization and selection in continuous integration," 
    26th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2017), Santa Barbara, CA, USA, 2017, pp. 12-22, 
    doi: 10.1145/3092703.3092709.
    Available at: https://dl.acm.org/doi/10.1145/3092703.3092709

"""

import numpy as np

def failcount(result, sc=None):
    
    no_scheduled = len(sc.scheduled_testcases)
    rewards = np.zeros(no_scheduled)

    if(len(result[8])>0):
        rank_04 = np.array(result[8])-1
        # Gives a reward only for the tests in the first 40% of the test set
        rewards[rank_04] = result[0]    

    ordered_rewards = []

    for tc in sc.testcases():
        try:
            idx = sc.scheduled_testcases.index(tc)
            ordered_rewards.append(rewards[idx])
        except ValueError:
            ordered_rewards.append(0.0)  # Unscheduled test case

    return ordered_rewards


def timerank(result, sc):
    if result[0] == 0:
        return 0.0

    total = result[0]
    rank_idx = np.array(result[7])-1
    no_scheduled = len(sc.scheduled_testcases)

    rewards = np.zeros(no_scheduled)
    rewards[rank_idx] = 1
    rewards = np.cumsum(rewards)  # Rewards for passed testcases
    rewards[rank_idx] = total  # Rewards for failed testcases

    ordered_rewards = []

    for tc in sc.testcases():
        try:
            idx = sc.scheduled_testcases.index(tc)  # Slow call
            ordered_rewards.append(rewards[idx])
        except ValueError:
            ordered_rewards.append(0.0)  # Unscheduled test case

    return ordered_rewards


def tcfail(result, sc):
    
    if (result[0] == 0)|(len(result[8])>0):
        return 0.0

    rank_04 = np.array(result[8])-1
    rank_idx = np.array(result[7])-1
    no_scheduled = len(sc.scheduled_testcases)

    rewards = np.zeros(no_scheduled)
    for i in rank_idx:
        # Gives a reward only for the tests in the first 40% of the test set
        if(i in rank_04):
            rewards[i] = 1

    ordered_rewards = []

    for tc in sc.testcases():
        try:
            idx = sc.scheduled_testcases.index(tc)
            ordered_rewards.append(rewards[idx])
        except ValueError:
            ordered_rewards.append(0.0)  # Unscheduled test case

import numpy as np

def failcount(result, sc=None):
    
    no_scheduled = len(sc.scheduled_testcases)
    rewards = np.zeros(no_scheduled)

    if(len(result[8])>0):
        rank_04 = np.array(result[8])-1
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
        if(i in rank_04):
            rewards[i] = 1

    ordered_rewards = []

    for tc in sc.testcases():
        try:
            idx = sc.scheduled_testcases.index(tc)
            ordered_rewards.append(rewards[idx])
        except ValueError:
            ordered_rewards.append(0.0)  # Unscheduled test case

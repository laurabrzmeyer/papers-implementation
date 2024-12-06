"""
RL METHOD

Implementation by Maria Laura Brzezinski Meyer
Last modification: 06-12-2024

References:
    T. Shi, L. Xiao, and K. Wu,  
    "Reinforcement Learning Based Test Case Prioritization for Enhancing the Security of Software,"
    2020 IEEE 7th Int. Conf. on Data Science and Advanced Analytics (DSAA), Sydney, NSW, Australia, 2020, pp. 663-672,   
    doi: 10.1109/DSAA49011.2020.00076.
    Available at: https://ieeexplore.ieee.org/document/9260075

"""

import numpy as np

class RewardCycle():
    def __init__(self, scenario, reward_name, rank_sel):
        self.cycle = scenario.cycle
        self.testcases = scenario.gen_testcases
        self.no_testcases = len(self.testcases)
        self.solutions = scenario.solutions
        self.RewardType = reward_name.split('_') # Ex: rhe_whole_all / the_part_four
        self.rank_sel = rank_sel
        self.test_id = dict()
        self.reward = dict()
        self.T = self.init_T()
        self.matrix = self.init_matrix()
        self.init_reward()

    def weight(self, x):
        if(self.RewardType[0]=='rhe'):
            return max(0.0, x)
        elif(self.RewardType[0]=='the'):
            return np.tanh(x)

    def init_T(self):
        if(self.RewardType[1]=='whole'):
            return {i['ID']: 1 for i in self.testcases}
        elif(self.RewardType[1]=='part'):
            return {i['ID']: self.solutions[i['ID']] for i in self.testcases}
        else:
            assert 0==1, 'Error in reward name!'

    def init_matrix(self):
        if(self.RewardType[2]=='all'):
            return np.ones((self.no_testcases, self.cycle-1))
        elif(self.RewardType[2]=='four'):
            if(self.cycle<5):
                return np.ones((self.no_testcases, self.cycle-1))
            else:
                return np.ones((self.no_testcases, 4))
        else:
            assert 0==1, 'Error in reward name!'

    def init_reward(self):

        i = 0

        for tc in self.testcases:

            self.test_id[tc['Test']] = i
            lr = tc['LR'].copy()

            if(len(lr)>0):
                if(len(lr)>=4):
                    if(self.RewardType[2]=='four'):
                        lr = lr[0:4]

                lr.reverse()
                self.matrix[i] = lr

                self.reward[tc['Test']] = (sum([lr[i]*self.weight(i+1) for i in range(0,len(lr))]))*self.T[tc['ID']]
        
            else:
                self.reward[tc['Test']] = 0

            i+=1

    def get_reward(self):
        ordered_reward = []
        for tc in self.testcases:
            if(tc['Test'] in self.rank_sel):
                ordered_reward.append(self.reward[tc['Test']])
            else:
                ordered_reward.append(0)
        return ordered_reward
    
class Reward():
    def __init__(self, reward_name):
        self.__name__ = reward_name
        self.reward_cycle = None
    def generat_reward(self, result, sc):
        self.reward_cycle = RewardCycle(sc, self.__name__, result[-1])
        return self.reward_cycle.get_reward()
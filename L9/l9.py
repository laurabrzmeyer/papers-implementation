"""
COLEMAN

Implementation by Maria Laura Brzezinski Meyer
Last modification: 06-12-2024

References:
    J. A. P. Lima and S. R. Vergilio, 
    "A Multi-Armed Bandit Approach for Test Case Prioritization in Continuous Integration Environments,"
    in IEEE Transactions on Software Engineering, vol. 48, no. 2, pp. 453-465, 1 Feb. 2022, 
    doi: 10.1109/TSE.2020.2992428. 
    Available at: https://ieeexplore.ieee.org/document/9086053
    
"""

from memory import MomentaryMemory, CumulativeMemory, SumMemory, MemoryExperiment
from policy import EpsilonGreedy, UCB, FRRMAB
from reward import RNFailReward, TimeRankReward

"""
POLICIES SETTINGS:
    EpsilonGreedy --> requires epsilon to balance exploration vs. explotation
        policy_settings={'Type':'Egreedy', 'epsilon':0.3}
    UCB --> requires coeficient C to balance exploration vs. explotation
        policy_settings={'Type':'UCB', 'C':0.3}
    FRRMAB --> requires coeficient C and decay factor
        policy_settings={'Type':'FRRMAB', 'C':0.3, 'DF':1.0}
"""

class L9():

    def __init__(self, variant_name, data_input, win_size=20, policy_settings={'Type':'FRRMAB', 'C':0.3, 'DF':1.0}, reward_type='TRR'):
        self.variant_name = variant_name
        self.INP = data_input
        self.win_size = win_size
        self.agent = self.creat_agent(policy_settings, reward_type)
        self.momen_memory = MomentaryMemory()
        self.cumul_memory = CumulativeMemory(self.win_size)
        self.sum_memory = SumMemory()
        self.df_prios = pd.DataFrame()

    """
    Function to creat the MAB agent
    ...

    Parameters
    ----------
    policy_settings : dict
        dictionary with all parameters required by the policy

    reward_type : str
        name of the reward, it can be TRR or RNF

    Return
    ----------
    agent : dict
        dictionary with policy and reward objects
    """ 
    def creat_agent(self, policy_settings, reward_type):

        pol_name = policy_settings['Type']
        if(pol_name=='Egreedy'):
            self.policy = EpsilonGreedy(policy_settings['epsilon'])
        elif(pol_name=='UCB'):
            self.policy = UCB(policy_settings['C'])
        elif(pol_name=='FRRMAB'):
            self.policy = FRRMAB(policy_settings['C'], policy_settings['DF'])
        else:
            assert 0==1, "Policy not available!"

        if(reward_type=='RNF'):
            self.reward = TimeRankReward()
        elif(reward_type=='TRR'):
            self.reward = RNFailReward()
        else:
            assert 0==1, "Reward not available!"
        
        agent = {'policy':self.policy, 'reward':self.reward}

        return agent

    """
    Function to prioritize the tests
    ...

    Parameters
    ----------
    test_set : list
        list of the ids of the tests to be prioritized
        if None, it will take the self.tcs_available

    Return
    ----------
    tcs_ordered : list
        list of tests' ids ordered by their priorities
    """
   def get_prio(self, selection=None):

        cycle = self.INP.in_cycle
        tc_available = self.INP.tc_available
        self.momen_memory.update_memory(tc_available, cycle)

        # If first cycle
        if cycle == min(self.INP.in_cycle):
            random.shuffle(tc_available)
            actions = tc_available
        else:
            actions = self.policy.choose(tc_available, self.sum_memory)

        prio_list = [a for a in actions if a in tc_available]
        if(selection!=None):
          sel_list = prio_list[0:selection]
        else:
          sel_list = prio_list
        rewards, ranks = self.reward.evaluate(actions, sel_list, self.INP.present)
        self.policy.observe(self.momen_memory, actions, rewards)
        self.policy.credit_assignment(self.momen_memory, self.cumul_memory, self.sum_memory)

        return order

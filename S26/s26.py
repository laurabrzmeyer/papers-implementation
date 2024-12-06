"""
FAZ and EXTFAZ METHODs

Implementation by Maria Laura Brzezinski Meyer

References:

    E. Engström, P. Runeson and A. Ljung, 
    "Improving Regression Testing Transparency and Efficiency with History-Based Prioritization -- An Industrial Case Study," 
    2011 Fourth IEEE International Conference on Software Testing, Verification and Validation, Berlin, Germany, 2011, pp. 367-376, 
    doi: 10.1109/ICST.2011.27.
    Available at: https://ieeexplore.ieee.org/document/5770626

    Y. Fazlalizadeh, A. Khalilian, M. Azgomi and S. Parsa, 
    "Prioritizing test cases for resource constraint environments using historical test case performance data", 
    2009 2nd IEEE International Conference on Computer Science and Information Technology, pp. 190-195, 2009,
    doi: 10.1109/ICCSIT.2009.5234968.
    Availble at: https://ieeexplore.ieee.org/abstract/document/5234968

"""

import pandas as pd
import numpy as np

class S26():
    '''
    variant_name = name for variant, to get predifined ones: S26.1.1, S26.1.2, S26.2.1, and S26.2.2
    win_size = size of window in cycles (int value)
    INP = object from input_data class
    specification = dictionary in the following the format {'alpha':float, 'beta':float, 'gamma':float}
    '''
    def __init__(self, variant_name, data_input, win_size=5, specification=None):
        self.variant_name = variant_name
        self.INP = data_input
        self.win_size = win_size
        self.df_prio = pd.DataFrame()   # to save dataframe with tests priorities
        self.init_S26(specification)

    def init_S26(self, specification):

        if((specification==None)):
            self.alpha = 0.04   # weight for the history effectiveness criterion
            self.beta = 0.7     # weight for the past priority value criterion
            self.gamma = 0.7    # weight for the unexecution counter criterion
        else:
            assert (('alpha' in list(specification.keys()))&('beta' in list(specification.keys()))&('gamma' in list(specification.keys()))), 'Error! Please provide the specification parameter as a dictionary in the following format:{"alpha":float, "beta":float, "gamma":float}.'
            self.alpha = specification['alpha']
            self.beta = specification['beta']
            self.gamma = specification['gamma']

        if(self.variant_name.endswith('1')):
            self.win_size = 10000

        self.LastPrio = {}
        self.ExecCounter = {}
        for tc in self.data_input.test_catalog:
            if('StaticPrio' in self.data_input.columns_in_data):
                self.LastPrio[tc] = self.get_static_prio(tc)
            else:
                self.LastPrio[tc] = 0
            self.ExecCounter = 0

        self.check_input()

    def check_input(self):
        required_data = ['Test', 'Cycle', 'Result']
        if(self.variant_name.startswith('S26.2')):
            required_data.append('StaticPrio')
            required_data.append('TestAge')
        data_columns = self.INP.columns_in_data
        missing = set(required_data) - set(data_columns)
        assert len(missing)==0, 'Error in input data! Missing the following column(s):{}'.format(missing)


    def get_fail_rate(self, test):
        past = self.INP.past.copy()
        c = self.INP.get_current_cycle()
        win = past[past['Cycle']>=(c-self.win_size)]
        t_execs = win[win['Test']==test]
        if(len(t_execs)==0):
            fail_rate = 0
        else:
            faults_found = t_execs[t_execs['Result']==1]
            fail_rate = len(faults_found)/len(t_execs)
        return fail_rate
    
    def get_age_prio(self, test):
        present = self.INP.present.copy()
        tc_info = present[present['Test']==test]
        return list(tc_info['TestAge'])[0]
    
    def get_static_prio(self, test):
        present = self.INP.present.copy()
        tc_info = present[present['Test']==test]
        return list(tc_info['StaticPrio'])[0]

    '''
    Function to prioritize the tests at the present cycle
    '''
    def get_prio(self, selection==None):                       
            
        P = []

        ### PRIORITIZATION
        for tc in self.INP.tc_availables:
            hist_eff = self.get_fail_rate(tc)
            P_tc = self.alpha*hist_eff + self.beta*self.LastPrio[tc] + self.gamma*self.ExecCounter[tc]
            if(self.variant_name.startswith('S26.2')):
                N = self.get_age_prio(tc)
                I = self.get_static_prio(tc)
                P_tc = P_tc + N + I
            P.append(P_tc)
            self.LastPrio[tc] = P_tc

        df = pd.DataFrame({'Test':self.INP.tc_availables, 'Priority':P})
        
        # Need to cut if selection != None to calculate self.ExecCounter
        if(selction!=Non):
            self.df_prio = df.sort_values(by='Priority', ascending=False).copy()[0:selection]
        else:
            self.df_prio = df.copy()
        
        for index, row in self.df_prio.iterrows():
            tc = row['Test']
            self.ExecCounter[tc] = self.ExecCounter[tc] + 1

        df = df.sample(frac=1).reset_index(drop=True)
        order = list(df.sort_values('Priority', ascending=False)['Test'])

        return order

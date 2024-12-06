"""
MF and ARM METHODs

Implementation by Maria Laura Brzezinski Meyer

References:

    D. Marijan, A. Gotlieb and S. Sen, 
    "Test Case Prioritization for Continuous Regression Testing: An Industrial Case Study," 
    2013 IEEE International Conference on Software Maintenance, Eindhoven, Netherlands, 2013, pp. 540-543, 
    doi: 10.1109/ICSM.2013.91.
    Availble at: https://ieeexplore.ieee.org/document/6676952

"""

import pandas as pd
import numpy as np

class S34():
    '''
    variant_name = name for variant, to get predifined ones: S3.1.1, S3.1.2, S3.2.1, and S3.2.2
    win_size = size of window in cycles (int value)
    INP = object from input_data class
    specification = dictionary in the following the format {'weights':list, 'tmax':float}
    '''
    def __init__(self, variant_name, data_input, win_size=3, specification=None):
        self.variant_name = variant_name
        self.INP = data_input
        self.win_size = win_size
        self.df_prio = pd.DataFrame()   # to save dataframe with tests priorities
        self.init_S34(specification)

    def init_S34(self, specification):

        if((specification==None)):
            self.weights = [0.7,0.2,0.1]   # list with values to weight each execution
            self.tmax = None
        else:
            assert ('weights' in list(specification.keys()))&('tmax' in list(specification.keys())), 'Error! Please provide the specification parameter as a dictionary in the following format:{"weights":list, "tmax":float}.'
            self.weights = specification['weights']
            self.tmax = specification['tmax']

        self.check_input()

    def check_input(self):
        required_data = ['Test', 'Cycle', 'Result']
        data_columns = self.INP.columns_in_data
        missing = set(required_data) - set(data_columns)
        assert len(missing)==0, 'Error in input data! Missing the following column(s):{}'.format(missing)

        '''
    Function to prioritize the tests at the present cycle
    '''
    def get_prio(self):

        i_len = self.win_size
        j_len = len(self.INP.tc_availables)
        MF = [[0 for _ in range(j_len)] for _ in range(i_len)]
        
        j = 0

        for t in self.INP.tc_availables:

            LR = self.get_last_results(t)

            for i in range(0, i_len):
                MF[i][j] = self.map_status(LR[i])
                j = j + 1 

        P = list((MF * self.weights[:, np.newaxis]).sum(axis=0))

        df = pd.DataFrame({'Test':self.INP.tc_availables, 'Priority':P})
        if(self.variant_name.endswith('1')):
            df = self.add_groups(df)
            df = self.add_time(df, self.INP.present)[['Test', 'Prio_ROCKET']].rename(columns={'Prio_ROCKET':'Priority'})

        self.df_prio = df.copy()

        df = df.sample(frac=1).reset_index(drop=True)
        order = list(df.sort_values('Priority', ascending=False)['Test'])

        return order

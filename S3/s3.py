"""
ROCKET METHOD

Implementation by Maria Laura Brzezinski Meyer
Last modification: 06-12-2024

References:
    D. Marijan, A. Gotlieb and S. Sen, 
    "Test Case Prioritization for Continuous Regression Testing: An Industrial Case Study," 
    2013 IEEE International Conference on Software Maintenance, Eindhoven, Netherlands, 2013, pp. 540-543, 
    doi: 10.1109/ICSM.2013.91.
    Available at: https://ieeexplore.ieee.org/document/6676952

"""

import pandas as pd
import numpy as np

class S3():
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
        self.init_S3(specification)

    def init_S3(self, specification):

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

    """
    Function to create the matrix of historical results
    ...

    Parameters
    ----------
    self.INP : input_data()
    self.win_size : int
    self.variant_name : str

    Return
    ----------
    LR : list
        list of past results of a test
    """  
    def get_last_results(self, test):
        past_data = self.INP.past.copy()
        exec_tc = past_data[past_data['Test']==test].sort_values(by='Cycle', ascending=False)
        if(self.variant_name.startswith('S3.1')):
            LR = list(exec_tc['Result'])[0:self.win_size]
            while(len(LR)<self.win_size):
                LR.append('NE')
        elif(self.variant_name.startswith('S3.2')):
            c = self.INP.get_current_cycle()
            list_int = [i for i in range((c-self.win_size),c)]  
            list_int.reverse()            
            LR = [list(exec_tc[exec_tc['Cycle']==i]['Result'])[0] if len(exec_tc[exec_tc['Cycle']==i])==1 else 'NE' for i in list_int]
        else:
            assert 0==1, 'Error! Variant not identified.'
        return LR
    
    """
    Function to transform test's status into a numerical value
    ...

    Parameters
    ----------
    status : int
        int that defines a test's status

    Return
    ----------
    rocket_status : int (-1, 0, or 1)
    """  
    def map_status(self, status):
        # If passed
        if(status==0):
            rocket_status = 1
        else:
            # If failed
            if(status==1):
                rocket_status = -1
            #Not executed
            else:
                rocket_status = 0 
        return rocket_status
    
    """
    Function to classify tests into groups according to their priority value
    ...

    Parameters
    ----------
    df : pd.DataFrame()
        a dataframe with two collumns: tests' ids and tests' priority

    Return
    ----------
    df : pd.DataFrame()
        a dataframe with three collumns: tests' ids, tests' priority and tests's group
    """ 
    def add_groups(self, df):
        df_classes = pd.DataFrame({'Class':sorted(set(df['Priority']))}).reset_index(drop=False)
        Prio_Class = []
        for index, row in df.iterrows():
            Class = row['Priority']
            prio = list(df_classes[df_classes['Class']==Class]['index'])[0] + 1
            Prio_Class.append(prio)
        df.insert(len(df.columns), "Prio_Class", Prio_Class, True)
        return df

    """
    Function to order tests of each groups according to their execution time
    ...

    Parameters
    ----------
    df : pd.DataFrame()
        a dataframe with three collumns: tests' ids, tests' priority and tests's group

    Return
    ----------
    df : pd.DataFrame()
        a dataframe with four collumns: tests' ids, tests' priority, tests's group and tests's final order
    """ 
    def add_time(self, df, present):
        if(self.tmax==None):
            self.tmax = sum(present['Duration'])
        P = []
        for index, row in df.iterrows():
            tc = row['Test']
            p = row['Prio_Class']
            duration = list(present[present['Test']==tc]['Duration'])[0]
            if(duration>self.tmax):
                t = max(df['Prio_Class'])
                p_new = t + 1
            else:
                p_new = p + (duration/self.tmax)
            P.append(p_new)
        df.insert(len(df.columns), "Prio_ROCKET", P, True)
        return df

    
    '''
    Function to prioritize the tests at the present cycle
    '''
    def get_prio(self, selection=None):

        i_len = self.win_size
        j_len = len(self.INP.tc_availables)
        MF = [[0 for _ in range(j_len)] for _ in range(i_len)]
        
        j = 0

        for tc in self.INP.tc_availables:

            LR = self.get_last_results(tc)

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

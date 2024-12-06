"""
TOPSIS METHOD

Implementation by Maria Laura Brzezinski Meyer
Last modification: 06-12-2024

References:

    Young-Jou Lai, Ting-Yun Liu, Ching-Lai Hwang,
    "TOPSIS for MODM,"
    European Journal of Operational Research, Volume 76, Issue 3, 1994, Pages 486-500, ISSN 0377-2217,
    doi: 10.1016/0377-2217(94)90282-8.
    Available at: https://www.sciencedirect.com/science/article/pii/0377221794902828

    Tahvili, S., Afzal, W., Saadatmand, M., Bohlin, M., Sundmark, D., Larsson, S. (2016).
    "Towards Earlier Fault Detection by Value-Driven Prioritization of Test Cases Using Fuzzy TOPSIS,"
    In: Latifi, S. (eds) Information Technology: New Generations. Advances in Intelligent Systems and Computing, vol 448. Springer, 
    doi: 10.1007/978-3-319-32467-8_65.
    Available at: https://doi.org/10.1007/978-3-319-32467-8_65

"""

import pandas as pd
import math

class S22():
    '''
    variant_name = name for variant, to get predifined ones: S22.1 and S22.2
    win_size = size of window in cycles (int value)
    INP = object from input_data class
    criteria_specif = list of tuples following the format (criteria_name:str, criteria_benefit:bool, criteria_weight:float)
    '''
    def __init__(self, variant_name, data_input, win_size=1000, criteria_specif=None):
        self.variant_name = variant_name
        self.INP = data_input
        self.win_size = win_size
        self.criteria = []              # list with name of criteria
        self.benefit = {}               # dictionary with a boolean value for each criterion (True if the aim is to maximize the criterion and False if is to minimize it)
        self.weights = {}               # dictionary with values to weight each criterion
        self.df_prio = pd.DataFrame()   # to save dataframe with tests priorities
        self.init_S22(criteria_specif)

    def init_S22(self, criteria_specif):

        if((criteria_specif==None)&(self.variant_name=='S22.1')):
            self.criteria = ['FailProb', 'ExecTime', 'ReqCov', 'TestCost']
            self.benefit = {'FailProb':True, 'ExecTime':False, 'ReqCov':True, 'Cost':False}
            self.weights = {'FailProb':1.0, 'ExecTime':1.0, 'ReqCov':1.0, 'Cost':1.0}
        elif((criteria_specif==None)&(self.variant_name=='S22.2')):
            self.criteria = ['FailProb', 'ExecTime', 'ReqCov', 'TestCost']
            self.benefit = {'FailProb':True, 'ExecTime':False, 'ReqCov':True, 'TestCost':False}
            self.weights = {'FailProb':1.0, 'ExecTime':0.0, 'ReqCov':1.0, 'TestCost':1.0}
        else:
            assert criteria_specif!=None, 'The variant provided is not defined yet! The criteria specification is required.'
            for c in criteria_specif:
                self.criteria.append(c[0])
                self.benefit[c[0]] = c[1]
                self.weights[c[0]] = c[2]

        self.check_input()

    def check_input(self):
        required_data = ['Test', 'Cycle', 'Result', 'ReqCov', 'TestCost']
        data_columns = self.INP.columns_in_data
        missing = set(required_data) - set(data_columns)
        assert len(missing)==0, 'Error in input data! Missing the following column(s):{}'.format(missing)
    
    def get_fail_detection_probability(self, test):   
        past = self.INP.past.copy()
        c = self.INP.get_current_cycle()
        win = past[past['Cycle']>=(c-self.win_size)]
        t_execs = win[win['Test']==test]
        if(len(t_execs)==0):
            fail_prob = 0
        else:
            faults_found = t_execs[t_execs['Result']==1]
            fail_prob = len(faults_found)/len(t_execs)
        return fail_prob

    def get_execution_time(self, test):
        # the test's execution time will be calculated by the mean of past durations
        past = self.INP.past.copy()
        past_t = past[past['Test']==test].sort_values(by='Cycle', ascending=False).reset_index(drop=True)
        ## to consider only PASS exeutions:
        # past_t = past[(past['Test']==test)&(past['Result']==0)].sort_values(by='Cycle', ascending=False).reset_index(drop=True)
        if(len(past_t)>0):
            exec_time = sum(past_t['Duration'])/len(past_t['Duration'])
        else:
            # if the test was not executed in the past, it's duration will be the one from its first execution
            future = self.INP.future.copy()
            future_t = future[future['Test']==test].sort_values(by='Cycle', ascending=True).reset_index(drop=True)
            assert len(future_t)>0, 'No data found for test {}! It is not possible to estimate the execution time.'.format(test)
            exec_time = list(future_t['Duration'])[0]
        return exec_time

    """
    Function to create the decision matrix with all criteria
    ...

    Parameters
    ----------
    self.INP : input_data()

    Return
    ----------
    DM : pd.DataFrame()
        dataframe with 5 columns: Test, FailProb, ExecTime, ReqCov, TestCost
    """ 
    def get_decision_matrix(self):

        present = self.INP.present.copy()
        tests = list(present['Test'])

        if('FailProb' not in self.INP.columns_in_data):
            FAIL_PROB = []
            for t in tests:
                FAIL_PROB.append(self.get_fail_detection_probability(t))
            present.insert(len(present.columns), "FailProb", FAIL_PROB, True)
        
        if('ExecTime' not in self.INP.columns_in_data):
            assert 'Duration' in self.INP.columns_in_data, 'Error! No execution duration provided in input data.'
            EXEC_TIME = []
            for t in tests:
                EXEC_TIME.append(self.get_execution_time(t))
            present.insert(len(present.columns), "ExecTime", EXEC_TIME, True)

        DM = present[['Test', 'FailProb', 'ExecTime', 'ReqCov', 'TestCost']]

        return DM
    
    """
    Function to normalize the values of criteria
    ...

    Parameters
    ----------
    DM : pd.DataFrame()
        decision matrix dataframe with 5 columns: Test, FailProb, ExecTime, ReqCov, TestCost

    Return
    ----------
    DM_Norm : pd.DataFrame()
        decision matrix dataframe with normalized criteria. It has 5 columns: Test, FailProb, ExecTime, ReqCov, TestCost
    """ 
    def normalization(self, DM):

        data = DM.copy(deep=True)

        sum_of_squares_FP = data['FailProb'].apply(lambda x: x ** 2).sum()
        if(sum_of_squares_FP>0):
            data.insert(len(data.columns), "FailProb_Norm", data['FailProb']/sum_of_squares_FP, True)
        else:
            data.insert(len(data.columns), "FailProb_Norm", data['FailProb'], True)

        sum_of_squares_Time = data['ExecTime'].apply(lambda x: x ** 2).sum()
        if(sum_of_squares_Time>0):
            data.insert(len(data.columns), "ExecTime_Norm", data['ExecTime']/sum_of_squares_Time, True)
        else:
            data.insert(len(data.columns), "ExecTime_Norm", data['ExecTime'], True)

        sum_of_squares_Req = data['ReqCov'].apply(lambda x: x ** 2).sum()
        if(sum_of_squares_Req>0):
            data.insert(len(data.columns), "ReqCov_Norm", data['ReqCov']/sum_of_squares_Req, True)
        else:
            data.insert(len(data.columns), "ReqCov_Norm", data['ReqCov'], True)

        sum_of_squares_Cost = data['TestCost'].apply(lambda x: x ** 2).sum()
        if(sum_of_squares_Cost>0):
            data.insert(len(data.columns), "TestCost_Norm", data['TestCost']/sum_of_squares_Cost, True)
        else:
            data.insert(len(data.columns), "TestCost_Norm", data['TestCost'], True)

        DM_Norm = data[['Test', 'FailProb_Norm', 'ExecTime_Norm', 'ReqCov_Norm', 'TestCost_Norm']]
        DM_Norm = DM_Norm.rename(columns={'FailProb_Norm':'FailProb', 'ExecTime_Norm':'ExecTime', 'ReqCov_Norm':'ReqCov', 'TestCost_Norm':'TestCost'})

        return DM_Norm
    
    """
    Function to weight the criteria
    ...

    Parameters
    ----------
    self.weights : list
    DM : pd.DataFrame()
        decision matrix dataframe with 5 columns: Test, FailProb, ExecTime, ReqCov, TestCost

    Return
    ----------
    DM_Weighted : pd.DataFrame()
        decision matrix dataframe with weighted criteria. It has 5 columns: Test, FailProb, ExecTime, ReqCov, TestCost
    """ 
    def weighting(self, DM):
        data = DM.copy(deep=True)
        criteria = list(self.weights.keys())
        for crit in criteria:
            data[crit+'_Weight'] = data[crit]*self.weights[crit]
        DM_Weight = data[['Test', 'FailProb_Weight', 'ExecTime_Weight', 'ReqCov_Weight', 'TestCost_Weight']]
        DM_Weight = DM_Weight.rename(columns={'FailProb_Weight':'FailProb', 'ExecTime_Weight':'ExecTime', 'ReqCov_Weight':'ReqCov', 'TestCost_Weight':'TestCost'})
        return DM_Weight

    """
    Function to calculate the positive ideal solution (PIS) and the negative ideal solution (NIS)
    ...

    Parameters
    ----------
    DM : pd.DataFrame()
        decision matrix dataframe with 5 columns: Test, FailProb, ExecTime, ReqCov, TestCost
    criterion : string
        name of criterion
    benefit : bool
        if True, criterion is benefit

    Return
    ----------
    PIS : float
        the positive ideal solution for the criterion
    NIS : float
        the negative ideal solution for the criterion
    """ 
    def calculation_PIS_NIS(self, decision_matrix, criterion, benefit=True):
        C = list(decision_matrix[criterion])
        if (benefit):
            PIS = max(C)
            NIS = min(C)
        else:
            PIS = min(C)
            NIS = max(C)
        return PIS, NIS
    
    '''
    Auxiliar function to calculate the distance between two points (a and b)
    '''
    def calculation_distance(self, a, b):
        return pow(a-b, 2)

    '''
    Auxiliar function to calculate the sqrt of the sum of distances
    '''
    def calculation_D(self, list_distances):
        return math.sqrt(sum(list_distances))

    '''
    Auxiliar function to calculate the coeficient of a test
    '''
    def calculation_Coef(self, D_plus, D_minus):
        if((D_minus+D_plus)==0):
            return 0
        return D_minus/(D_minus+D_plus)

    '''
    Function to prioritize the tests at the present cycle
    '''
    def get_prio(self):

        cycle = self.INP.cycle
        
        # Get Decision Matrix from cycle
        DM = self.get_decision_matrix(cycle)

        # Normalization
        DM_Norm = self.normalization(DM)

        # Weighting
        DM_Weight = self.weighting(DM_Norm)

        # Calculation of PIS and NIS
        PIS = {}
        NIS = {}
        for crit in self.criteria:
            pis, nis = self.calculation_PIS_NIS(DM_Weight, crit, benefit=self.benefit[crit])    
            PIS[crit] = pis
            NIS[crit] = nis
        P = []

        for tc in self.INP.tc_availables:
                
            row_tc = DM_Weight[DM_Weight['Test']==tc]

            # Calculation of the distance between test and PIS/NIS
            D_PIS = {}
            D_NIS = {}
            for crit in self.criteria:
                d_pis = self.calculation_distance(row_tc[crit].values[0], PIS[crit])
                d_nis = self.calculation_distance(row_tc[crit].values[0], NIS[crit])
                D_PIS[crit] = d_pis
                D_NIS[crit] = d_nis

            # Calculation of the D
            D_plus = self.calculation_D(list(D_PIS.values()))
            D_minus = self.calculation_D(list(D_NIS.values()))
                
            # Calculation of proximity coefficient
            CC = self.calculation_Coef(D_plus, D_minus)

            P.append(CC)

        df = pd.DataFrame({'Test':self.INP.tc_availables, 'Priority':P})
        
        self.df_prio = df.copy()

        df = df.sample(frac=1).reset_index(drop=True)
        order = list(df.sort_values('Priority', ascending=False)['Test'])

        return order

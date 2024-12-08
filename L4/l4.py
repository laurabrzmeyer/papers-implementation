"""
DeepOrder METHOD
* This script is an adaptation of Aizaz Sharif's ROCKET_on_Cisco.ipynb code 
* Accessed in April 2023
* Available at: https://github.com/T3AS/DeepOrder-ICSME21/blob/main/ROCKET_on_Cisco.ipynb

Implementation by Maria Laura Brzezinski Meyer
Last modification: 08-12-2024

References:
    A. Sharif, D. Marijan, and M. Liaaen, 
    "DeepOrder: Deep Learning for Test Case Prioritization in Continuous Integration Testing,"
    2021 IEEE Int. Conf. on Software Maintenance and Evolution (ICSME), pp. 525–534.
    Available at: https://arxiv.org/abs/2110.07443
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from datetime import datetime, date

class L4():
    '''
    variant_name = name for variant, to get predifined ones: L4.1, and L4.2
    data_path = path to dataframe
    '''
    def __init__(self, variant_name, data_path):
        self.variant_name = variant_name
        self.INP = self.contruction_inputDL_asCases(data_path)

    """
    Function to get last execution results
    ...

    Parameters
    ----------
    df : pd.DataFrame()

    Return
    ----------
    LastResults : list of int
    """  
    def get_lastresults(self, df):
        LastResults = []
        for index, row in df.iterrows():
            c = row['Cycle']
            tc = row['Test']
            previous_cycles = df[df['Cycle']<c]
            previous_cycles_tc = previous_cycles[previous_cycles['Test']==tc].sort_values(by='Cycle', ascending=False).reset_index(drop=True)
            LR = list(previous_cycles_tc['Result'])
            LastResults.append(LR)
        return LastResults
    
    """
    Function to get last run dates
    ...

    Parameters
    ----------
    df : pd.DataFrame()

    Return
    ----------
    LastRuns : list of int
    """  
    def get_lastruns(self, df):
        tfdf = df.copy()
        week = datetime.strptime("2020-01-08", "%Y-%m-%d")
        for c in list(df['Cycle'].unique()):
            tfdf.loc[tfdf['Cycle'] == c, ['Week']] = week
            week = week + timedelta(days=7)
        min_last_run = datetime.strptime("2020-01-01", "%Y-%m-%d")
        LastRuns = []
        for index, row in tfdf.iterrows():
            tc = row['Test']
            cycle = row['Cycle']
            past_data = tfdf[(tfdf['Test']==tc)&(tfdf['Cycle']<cycle)].sort_values(by='Week', ascending=False)
            past_runs = past_data['Week'].tolist()
            if(len(past_runs)>0):
                lrun = past_runs[0]
            else:
                lrun = min_last_run
            LastRuns.append(lrun)
        return LastRuns

    """
    Function to load data in the correct format
    ...

    Parameters
    ----------
    path : str
        path to the data

    Return
    ----------
    data : pd.DataFrame()
    """   
    def load_data(self, path):
        data = pd.read_csv(path, sep=';', dtype={'Cycle':int, 'Version':str, 'Test':str, 'Result':int, 'Duration':int})
        last_results = self.get_lastresults(data)
        data['LastResults'] = last_results
        last_runs = self.get_lastruns(data)
        data['LastRun'] = last_runs
        return data
    
    """
    Function to get last results of historical execution
    ...

    Parameters
    ----------
    df : pd.DataFrame()
    self.variant_name : str

    Return
    ----------
    E1 : int
        1st most recent result
    E2 : int
        2nd most recent result
    E3 : int
        3rd most recent result
    """   
    def get_Es_Cases(self, df):
        case = self.variant_name.split('.')[-1]
        E1, E2, E3 = ([] for j in range(3))
        last_results = df['LastResults'].values.tolist()
        if(case=='1'):
            for lr in last_results:
                Es = []
                i  = 0
                while(i<3):
                    if(len(lr)>0):
                        a = lr.pop(0)
                        Es.append(a)
                    else:
                        Es.append(-1)
                    i=i+1
                E1.append(Es[0])
                E2.append(Es[1])
                E3.append(Es[2])
        elif(case=='2'):
            for index, row in df.iterrows():
                execs_tc = df[df['Test']==row['Test']]
                Es = []
                for i in range(1,4):
                    lr = list(execs_tc[execs_tc['Cycle']==(row['Cycle']-i)]['Result'])
                    if(len(lr)>0):
                        assert len(lr) == 1
                        Es.append(lr[0])
                    else:
                        Es.append(-1)
                E1.append(Es[0])
                E2.append(Es[1])
                E3.append(Es[2])
        else:
            print('Case not available!')
            assert 1 == 0
        return E1, E2, E3
    
    """
    Function to convert results to -1 (if FAIL), 0 (if NOT EXECUTED), and 1 (if PASS)
    ...

    Parameters
    ----------
    e : int
        Result of test execution

    Return
    ----------
    inv_e : int
        Result of test execution according to ROCKET
    """  
    def EsDL_to_EsROCKET(self, e):
        if(e==1):    ## FAILED
            inv_e = -1
        elif(e==0):  ## PASSED
            inv_e = 1
        elif(e==-1): ## NOT EXECUTED
            inv_e = 0
        else:
            print('Error reverse_E')
        return inv_e
    
    """
    Function to convert last results
    ...
    
    Parameters
    ----------
    df : pd.DataFrame()

    Return
    ----------
    E1, E2, E3 : list of int
        Result of the last 3 execution of the test according to ROCKET
    """ 
    def get_Es_ROCKET(self, df):
        E1, E2, E3 = ([] for i in range(3))
        for index, row in df.iterrows():
            E1.append(self.EsDL_to_EsROCKET(row['E1']))
            E2.append(self.EsDL_to_EsROCKET(row['E2']))
            E3.append(self.EsDL_to_EsROCKET(row['E3']))
        return [E1,E2,E3]
    
    """
    Function to get the distance between the present and the last FAIL
    ...

    Parameters
    ----------
    df : pd.DataFrame()

    Return
    ----------
    distances_list : list of int
    """ 
    def get_distances(self, df):
        MF = df.loc[:,['E1_rocket', 'E2_rocket', 'E3_rocket']].values
        rows = len(MF)
        columns = len(MF[0])
        distances_list = []
        for i in range(rows):
            if -1 in MF[i]:
                for j in range(len(MF[i])):
                    if MF[i][j] == -1:
                        distances_list.insert(i, j+1)
                        break
            else:
                distances_list.insert(i, 0)
        return distances_list
    
    """
    Function to count number of changes in the last 3 execution results
    ...

    Parameters
    ----------
    df : pd.DataFrame()

    Return
    ----------
    change_in_status : list of int
    """ 
    def get_status_changes(self, df):
        MF = df.loc[:,['E1', 'E2', 'E3']].values
        rows = len(MF)
        change_in_status = []
        for i in range(rows):
            each_element = MF[i]
            counter = 0
            for j in range(len(each_element)-1):
                if each_element[j]!=each_element[j+1]:
                    counter+=1
            change_in_status.append(counter)
        return change_in_status

    """
    Function to get tests' priorities according to ROCKET
    ...

    Parameters
    ----------
    df : pd.DataFrame()

    Return
    ----------
    priority_value : list of float
    """ 
    def get_priority_value(self, df):
        data = df.copy()
        MF = data.loc[:,['E1_rocket', 'E2_rocket', 'E3_rocket']].values
        weights = np.array([0.7,0.2,0.1])
        Te = data.Duration.values
        priority_value = (MF*weights).sum(axis=1)
        priority_value += Te/np.max(Te)
        return priority_value
    
    """
    Function to organize run dates
    ...

    Parameters
    ----------
    df : pd.DataFrame()

    Return
    ----------
    Dates : list of str
    """ 
    def get_Dates(self, df):
        cycle = df.loc[:,'Cycle'].values
        Dates_np = df.loc[:,'LastRun'].values
        Dates = [pd.to_datetime(d) for d in Dates_np]
        rows = len(cycle)
        for i in range(rows):
            each_element = cycle[i]
            if i==0:
                dt = Dates[i]
                Dates[i] =  str(dt.year) +"-"+ str(dt.month) +"-"+ str(dt.day)
            if i >= 1:
                dt = Dates[i]
                value = float(each_element-1)
                dtt =  dt + timedelta(days=value)
                Dates[i] =  str(dtt.year) +"-"+ str(dtt.month) +"-"+ str(dtt.day)
        return Dates

    """
    Function to organize days in run dates
    ...

    Parameters
    ----------
    df : pd.DataFrame()

    Return
    ----------
    days : list of datetime.day
    """ 
    def get_days(self, Dates):
        currentDay = datetime.now().day
        currentMonth = datetime.now().month
        currentYear = datetime.now().year
        days=[]
        rows = len(Dates)
        for i in range(rows):
            if i == 0:
                #for 1st Cycle
                datenumpy = Dates[i]
                dt = pd.to_datetime(datenumpy)
                f_date = date(dt.year, dt.month, dt.day)
                l_date = date(currentYear,currentMonth,currentDay)
                delta = l_date - f_date
            if i >= 1:
                datenumpy = Dates[i]
                datenumpy_prev = Dates[i-1]
                dt = pd.to_datetime(datenumpy)
                dt_prev = pd.to_datetime(datenumpy_prev)
                f_date = date(dt.year, dt.month, dt.day)
                l_date = date(dt_prev.year, dt_prev.month, dt_prev.day)
                delta = l_date - f_date
            days.append(delta.days)
        return days

    """
    Function to construct the input to train the depp learning model
    ...

    Return
    ----------
    input_ : pd.DataFrame()
    """   
    def contruction_inputDL_asCases(self, data_path):

        input_ = self.load_data(data_path)

        ## E1, E2, E3
        E1, E2, E3 = self.get_Es_Cases(input_)
        input_['E1'] = E1
        input_['E2'] = E2
        input_['E3'] = E3
        input_['E1'] = input_['E1'].astype(int)
        input_['E2'] = input_['E2'].astype(int)
        input_['E3'] = input_['E3'].astype(int)

        ## E1, E2, E3 ROCKET
        E1_rocket, E2_rocket, E3_rocket = self.get_Es_ROCKET(input_)
        input_['E1_rocket'] = E1_rocket
        input_['E2_rocket'] = E2_rocket
        input_['E3_rocket'] = E3_rocket
        input_['E1_rocket'] = input_['E1_rocket'].astype(int)
        input_['E2_rocket'] = input_['E2_rocket'].astype(int)
        input_['E3_rocket'] = input_['E3_rocket'].astype(int)

        ## DIST
        distances_list = self.get_distances(input_)

        ## CHANGE_IN_STATUS
        change_in_status = self.get_status_changes(input_)

        ## PRIORITY_VALUE
        priority_value = self.get_priority_value(input_)

        input_['DIST'] = distances_list
        input_['CHANGE_IN_STATUS'] = change_in_status
        input_['PRIORITY_VALUE'] = priority_value

        ## Calculation of Dates
        Dates = self.get_Dates(input_)
        days = self.get_days(Dates)
        input_['LastRunFeature'] = days

        # Normalization
        input_["LastRunFeature"]=((input_["LastRunFeature"]-input_["LastRunFeature"].min())/(input_["LastRunFeature"].max()-input_["LastRunFeature"].min()))*5
        input_["DurationFeature"]=((input_["Duration"]-input_["Duration"].min())/(input_["Duration"].max()-input_["Duration"].min()))*5
        input_["Duration"] = input_["Duration"].astype(int)

        # ID
        input_['Id'] = range(1, 1+len(input_))

        return input_

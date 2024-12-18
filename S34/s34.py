"""
MF and ARM METHODs

Implementation by Maria Laura Brzezinski Meyer
Last modification: 06-12-2024

References:
    J. Anderson, S. Salem and H. Do,
    "Improving the effectiveness of test suite through mining historical data,"
    2014 11th Working Conf. on Mining Software Repositories (MSR), pp. 142–151, 
    doi: 10.1145/2597073.2597084.
    Available at: https://dl.acm.org/doi/10.1145/2597073.2597084

"""

import pandas as pd
import numpy as np
import random
from mlxtend.frequent_patterns import apriori, association_rules

class S34():
    '''
    variant_name = name for variant, to get predifined ones: S34.1.1, S34.1.2, S34.2.1, and S34.2.2
    win_size = size of window in cycles (int value)
    INP = object from input_data class
    specification = dictionary in the following the format {'support':float}
    '''
    def __init__(self, variant_name, data_input, win_size=3, specification=None):
        self.variant_name = variant_name
        self.INP = data_input
        self.win_size = win_size
        self.df_prio = pd.DataFrame()   # to save dataframe with tests priorities
        self.init_S34(specification)

    def init_S34(self, specification):
        if(self.variant_name.startswith('S34.2')):
            self.basket_set = self.construct_bs()
            if((specification==None)):
                self.support = 0.1
            else:
                assert 'support' in list(specification.keys()), 'Error! Please provide the specification parameter as a dictionary in the following format:{"weights":list, "tmax":float}.'
            self.support = specification['support']
        self.check_input()

    def check_input(self):
        required_data = ['Test', 'Cycle', 'Result']
        data_columns = self.INP.columns_in_data
        missing = set(required_data) - set(data_columns)
        assert len(missing)==0, 'Error in input data! Missing the following column(s):{}'.format(missing)

    """
    Function to get fail rate of a test
    """
    def get_fail_rate(self, test):
        history = self.INP.past
        cycle = self.INP.in_cycle
        if(self.win_size!=None):
            history = history[history['Cycle']>=(cycle-self.win_size)]
        if(cycle>self.win_size):
            assert len(history['Cycle'].unique())==self.win_size
        else:
            assert len(history['Cycle'].unique())<=self.win_size
        tc_win = history[history['Test']==test]
        n_executed = len(tc_win[(tc_win['Result']==1)|(tc_win['Result']==0)])
        n_failed = len(tc_win[tc_win['Result']==1])
        if(n_executed>0):
            rate = n_failed/n_executed
        else:
            rate = 0
        return rate

    """
    Function to construct the basket set
    """
    def construct_bs(self):
        cycles = self.INP.cycles
        tests = self.INP.test_catalog
        basket_set = pd.DataFrame(0, index=cycles, columns=tests) 
        for index, row in self.INP.data.iterrows():
            if(row['Result']==1):
                basket_set.loc[row['Test'], row['Cycle']] = 1
        return basket_set

    """
    Function to filter association rules
    """
    def filter_associations(self, association_results):
        LHS, RHS, SUP, CONF = ([] for i in range(4))
        for index, row in association_results.iterrows():
            a, = row['antecedents']
            c, = row['consequents']
            conf = row['confidence']
            sup = row['support']
            LHS.append(a)
            RHS.append(c)
            SUP.append(sup)
            CONF.append(conf)
        df_association = pd.DataFrame({'LHS':LHS, 'RHS':RHS, 'Support':SUP, 'Confidence':CONF})
        return df_association
    
    """
    Function to get association rules
    """
    def get_association_apriori(self, cols):
        c = self.INP.in_cycle
        if(self.win_size!=None):
            if(c<=self.win_size):
                bs = self.basket_set.iloc[1:c]
            else:
                bs = self.basket_set.iloc[(c-self.win_size):c]
        else:
            bs = self.basket_set
        bs = bs[cols].loc[:, (bs != 0).any(axis=0)]
        if(bs.shape[1]!=0):
            frequent_itemsets = apriori(bs.astype('bool'), min_support=self.support, use_colnames=True, max_len=2)
            rules = association_rules(frequent_itemsets, metric="confidence")
            df_asso = self.filter_associations(rules)
        else:
            df_asso = pd.DataFrame({'LHS':[], 'RHS':[], 'Support':[], 'Confidence':[]})
        return df_asso

    '''
    Function to prioritize the tests at the present cycle
    '''
    def get_prio(self, selection=None):

        tcs_available = self.INP.tc_availables
        
        P = []
        if(self.variant_name.startswith('S34.1')):
            for t in self.INP.tc_availables:
                prio = self.get_fail_rate(t)
                P.append(prio)
        elif(self.variant_name.startswith('S34.2')):
            smokes = random.sample(tcs_available, round(len(tcs_available)*0.2))
            association_cycle = self.get_association_apriori(tcs_available)
            for t in tcs_available:
                if(t in smokes):
                    prio = (2*len(smokes))
                    P.append(prio)
                else:
                    assoc_smoke = association_cycle[association_cycle['LHS'].isin(smokes)]
                    conf = list(assoc_smoke[assoc_smoke['RHS']==t]['Confidence'])
                    prio = sum(conf)
                    P.append(prio)
        else:
            assert 0==1, f'Variant {self.varian_name} not available!'

        df = pd.DataFrame({'Test':self.INP.tc_availables, 'Priority':P})
        self.df_prio = df.copy()

        df = df.sample(frac=1).reset_index(drop=True)
        order = list(df.sort_values('Priority', ascending=False)['Test'])

        return order

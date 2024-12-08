import pandas as pd

class input_data():

    def __init__(self, name, data_input=None, path_input=None):
        self.name = name
        self.data = data_input
        self.path = path_input

    def init_input(self):
        if(self.data==None):
            self.load_data()
        self.columns_in_data = list(self.data.columns)
        self.cycles = list(self.data['Cycle'].unique())
        self.cycles.sort()
        self.in_cycle = 0
        self.present = self.data[self.data['Cycle']==self.cycles[self.in_cycle]]
        self.tc_availables = list(self.present['Test'])
        self.past = self.data[self.data['Cycle']<self.cycles[self.in_cycle]]
        self.future = self.data[self.data['Cycle']>self.cycles[self.in_cycle]]
        self.test_catalog = list(self.data['Test'].unique())

    def load_data(self):
        assert self.path!=None, 'Not possible to load data! Please define the file path.'
        self.data = pd.read_csv(self.path, sep=';')

    '''
    Auxiliar function to get present cycle
    '''
    def get_current_cycle(self):
        return self.cycles[self.in_cycle]
    
    '''
    Auxiliar function to get version
    '''
    def get_current_version(self):
        v = self.present['Version'].unique()
        return list(v)[0]
    
    '''
    Auxiliar function to set the Result of not selected tests as not executed in case of selection
    '''
    def update_past(self, selection):
        not_executed_tests = set(self.tc_availables) - set(selection)
        self.data.loc[(self.data['Cycle']==self.in_cycle)&(self.data['Test'].isin(not_executed_tests)), ['Result']] = -1

    '''
    Auxiliar function to move to next cycle
    '''
    def next_cycle(self):
        self.in_cycle += 1 
        self.present = self.data[self.data['Cycle']==self.cycles[self.in_cycle]]
        self.tc_availables = list(self.present['Test'])
        self.past = self.data[self.data['Cycle']<self.cycles[self.in_cycle]]
        self.future = self.data[self.data['Cycle']>self.cycles[self.in_cycle]]

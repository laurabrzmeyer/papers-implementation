class MomentaryMemory():

    def __init__(self):
        self.memory_columns = ['Test', 'ActionsAttempt', 'ValueEstimates', 'T']
        self.memory = pd.DataFrame(columns=self.memory_columns)        

    def reset_memory(self, tcs, cycle):
        self.memory = pd.DataFrame({'Test':tcs, 'ActionsAttempt':[0.0]*len(tcs), 'ValueEstimates':[0]*len(tcs), 'T':[cycle]*len(tcs)})

class CumulativeMemory():

    def __init__(self, sw):
        self.memory_columns = ['Test', 'ActionsAttempt', 'ValueEstimates', 'T']
        self.memory = pd.DataFrame(columns=self.memory_columns)        
        self.win = sw

    def update_memory(self, momentary_memory):

        # Upadate Cumulative Memory
        if(len(self.memory)>0):
            self.memory = pd.concat([self.memory, momentary_memory.memory], ignore_index=True)
        else:
            self.memory = momentary_memory.memory.copy()

        unique_t = self.memory['T'].unique()
        if len(unique_t) > self.win:
            # Remove older
            min_t = max(unique_t) - self.win
            self.memory = self.memory[self.memory['T'] > min_t]

class SumMemory():

    def __init__(self):
        self.memory_columns = ['Test', 'ActionsAttempt', 'ValueEstimates', 'T', 'Q']
        self.memory = pd.DataFrame(columns=self.memory_columns)

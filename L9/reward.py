class RNFailReward():
    
    def __str__(self):
        return 'Time-ranked Reward'

    def get_name(self):
        return 'timerank'

    def evaluate(self, prio, present):
        
        total = sum(present['Result'])
        ranks = []
        
        if total == 0:
            return [{tc:0 for tc in prio}, ranks]
        rewards = {}
        position = 1
        
        for tc in prio:
            res = list(present[present['Test']==tc]['Result'])
            assert len(res) == 1
            if res[0] == 1:
                rewards[tc] = 1
                ranks.append(position)
            else:
                rewards[tc] = 0
            position = position + 1
        
        return [rewards, ranks]

class TimeRankReward():
    
    def __str__(self):
        return 'Time-ranked Reward'

    def get_name(self):
        return 'timerank'

    def evaluate(self, prio, present):
        
        total = sum(present['Result'])
        ranks = []
        
        if total == 0:
            return [{tc:0 for tc in prio}, ranks]
        
        rbf_rewards = {}
        position = 1
        for tc in prio:
            res = list(present[present['Test']==tc]['Result'])
            assert len(res) == 1
            if res[0] == 1:
                rbf_rewards[tc] = 1
                ranks.append(position)
            else:
                rbf_rewards[tc] = 0
            position = position + 1
            
        rewards = {}
        position = 0
        for tc in rbf_rewards:
            if(rbf_rewards[tc]==1):
                rewards[tc] = sum(list(rbf_rewards.values()))
            else:
                prev_tcs = list(rbf_rewards.values())[0:position]
                rewards[tc] = sum(prev_tcs)
            position = position + 1
        
        return [rewards, ranks]

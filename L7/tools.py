"""
RETECS METHOD
* This script was created to evaluate the prioritization of test cases to calculate the agent's reward

Implementation by Maria Laura Brzezinski Meyer
Last modification: 06-12-2024

References:
    H. Spieker, A. Gotlieb, D. Marijan, and M. Mossige, 
    "Reinforcement learning for automatic test case prioritization and selection in continuous integration," 
    26th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2017), Santa Barbara, CA, USA, 2017, pp. 12-22, 
    doi: 10.1145/3092703.3092709.
    Availble at: https://dl.acm.org/doi/10.1145/3092703.3092709

"""

def rank_verdict(sorted_tc, available_time, solutions, scheduled_testcases, ASC=False):

    scheduled_time = 0
    detection_ranks = []
    undetected_failures = 0
    rank_counter = 1
    order = []
    unscheduled_tests = []

    if(ASC):

        for row in sorted_tc:

            if scheduled_time + row['Duration'] <= available_time:
                try:
                    if solutions[row['ID']]:
                        detection_ranks.append(rank_counter)
                except:
                    pass
                scheduled_time += row['Duration']
                scheduled_testcases.append(row)
                order.append(row['Test'])
                rank_counter += 1
            else:
                undetected_failures += solutions[row['ID']]
                unscheduled_tests.append(row['Test'])

    else:

        while sorted_tc:

            cur_tc = sorted_tc.pop()

            if scheduled_time + cur_tc['Duration'] <= available_time:
                if solutions[cur_tc['ID']]:
                    detection_ranks.append(rank_counter)
                scheduled_time += cur_tc['Duration']
                scheduled_testcases.append(cur_tc)
                order.append(cur_tc['Test'])
                rank_counter += 1
            else:
                undetected_failures += solutions[cur_tc['ID']]
                unscheduled_tests.append(cur_tc['Test'])

    detected_failures = len(detection_ranks)
    total_failure_count = sum(solutions.values())

    return [detection_ranks, undetected_failures, order, scheduled_testcases, detected_failures, unscheduled_tests, total_failure_count]

def get_bugs(data, solutions=None, row=False):

    bugs_in_data = []
    
    if(row):
        b_list = data.replace('[','').replace(']','').replace('\'','').split(', ')
        for b in b_list:
            if(b!=''):
                if(b in bugs_in_data):
                    pass
                else:
                    bugs_in_data.append(b)

    else:
        for row in data:
            if(solutions[row['ID']]):
                bugs = row['Bugs'].replace('[','').replace(']','').replace('\'','').split(', ')
                for b in bugs:
                    if(b!=''):
                        if(b in bugs_in_data):
                            pass
                        else:
                            bugs_in_data.append(b)

    return bugs_in_data

def rank_bugs(sorted_tc, available_time, solutions, scheduled_testcases, ASC=False):

    bugs_in_data = get_bugs(sorted_tc, solutions)

    scheduled_time = 0
    detection_ranks = []
    undetected_failures = 0
    rank_counter = 1
    order = []
    bugs_already_know = []
    unscheduled_tests = []

    if(ASC):
        
        for row in sorted_tc:
            
            if scheduled_time + row['Duration'] <= available_time:
                # If Issue or Issue_Ref == 1
                if(solutions[row['ID']]):              
                    b = get_bugs(row['Bugs'], row=True)
                    if(len(b)>0):
                        if(len(set(b)-set(bugs_already_know))>0):
                            detection_ranks.append(rank_counter)
                            bugs_already_know = list(set(bugs_already_know + b))
                scheduled_time += row['Duration']
                scheduled_testcases.append(row)
                order.append(row['Test'])
                rank_counter += 1
            else:
                undetected_failures += solutions[row['ID']]
                unscheduled_tests.append(row['Test'])

    else:

        while sorted_tc:

            cur_tc = sorted_tc.pop()

            if scheduled_time + cur_tc['Duration'] <= available_time:
                # If Issue or Issue_Ref == 1
                if(solutions[cur_tc['ID']]): 
                    b = get_bugs(cur_tc['Bugs'], row=True)
                    if(len(b)>0):
                        if(len(set(b)-set(bugs_already_know))>0):
                            detection_ranks.append(rank_counter)
                            bugs_already_know = list(set(bugs_already_know + b))
                scheduled_time += cur_tc['Duration']
                scheduled_testcases.append(cur_tc)
                order.append(cur_tc['Test'])
                rank_counter += 1
                
            else:
                b = get_bugs(cur_tc['Bugs'], row=True)
                if(len(b)>0):
                    if(len(set(b)-set(bugs_already_know))>0):
                        undetected_failures += solutions[cur_tc['ID']]
                        bugs_already_know = list(set(bugs_already_know + b))
                unscheduled_tests.append(cur_tc['Test'])

    total_failure_count = len(bugs_in_data)  
    detected_failures = len(bugs_already_know)  

    return [detection_ranks, undetected_failures, order, scheduled_testcases, detected_failures, unscheduled_tests, total_failure_count]

def get_rank_selection(sorted_tc, available_time, NTC=False):

    scheduled_time = 0
    rank_counter = 1
    rank_sel = []
    unscheduled_ranks = []

    if(NTC==True):
        
        while sorted_tc:
            cur_tc = sorted_tc.pop()
            if scheduled_time + 1 <= available_time:
                rank_sel.append(rank_counter)
                scheduled_time += 1
            else:
                unscheduled_ranks.append(rank_counter)
            rank_counter += 1

    else:

        while sorted_tc:
            cur_tc = sorted_tc.pop()
            if scheduled_time + cur_tc['Duration'] <= available_time:
                rank_sel.append(rank_counter)
                scheduled_time += cur_tc['Duration']
            else:
                unscheduled_ranks.append(rank_counter)
            rank_counter += 1

    return [rank_sel, unscheduled_ranks]
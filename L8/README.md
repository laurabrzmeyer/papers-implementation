# L8 ALGORITHM

Welcome! This is the implementation of the **RL** method.

## Devellopers

- [ ] [Maria Laura BRZEZINSKI MEYER](https://github.com/laurabrzmeyer)

## Based on RETECS' original code

- Based on the version available in March 2023
- [ ] [RETECS](https://bitbucket.org/HelgeS/retecs/src/master/)

## RL Description

Reinforcement learning is also used by T. Shi et al. (2020). The strategy presented is also based on the principle that it is important to consider the execution history of test cases from previous cycles when ordering them in the current cycle. 
Therefore, they propose new reward functions based on the execution history, aiming to improve the ***TCFail*** reward from **RETECS** (**L7**). They use the same agents as the ones described in **L7**.

The reward functions are the weighted sum of the previous scores of each test, as shown in the equation below. 
The authors consider the verdict to be "fail" if a test is not executed. The rewards differ according to the weight function *w(x)* and the quantity of past information used.

> <img width="250" alt="image" src="https://github.com/user-attachments/assets/448ad064-bd15-4355-b906-a7559b2e9868">

The first weight function is *Relu*: *w(x) = relu(x) = max(0,x)*, (*x* ≤ 0). The reward is called *ReLu-Weighted Historical Execution Information Reward*, or ***RHE*** reward for short. It is represented by the following eqaution:

> <img width="250" alt="image" src="https://github.com/user-attachments/assets/002dccce-6157-4ea6-9594-61dd27dcb55b">

The entire historical record can be utilized, with $i$ increasing until all previous cycles are encompassed (*m=all*). Alternatively, *i* can be incremented from 0 to 4, focusing on the four most recent cycles (*m=4*). Besides that, just a partial reward can be considered, that is, the agent will receive a reward only if the test fails. These constraints led us to four types of rewards:

> <img width="400" alt="image" src="https://github.com/user-attachments/assets/b8ffb475-b98b-4852-9a38-c4d2e8a6d746">

The other weight function chosen by the authors is based on *Tanh* and named *Reward Function Based on Tanh Weighted Historical Execution Information of Test Cases* (***THE***). Therefore, *w(x) = tahn(x) = e<sup>x</sup> - e<sup>-x</sup>/e<sup>x</sup> + e<sup>-x</sup>*, (0 ≤ *x* ≤ 4). The following equation can be considered:

> <img width="250" alt="image" src="https://github.com/user-attachments/assets/5cec10ab-895d-4fcc-a15b-0ee68e2a2ac8">

As for ***RHE***, ***THE*** can be calculated for all tests (first equation below) or just for the failed ones (second equation below).

> <img width="400" alt="image" src="https://github.com/user-attachments/assets/41b8712a-299d-41ab-95ce-49c5f853f6e4">

For implementation, we used the same code as **RETECS**. The number of actions and the exploration rate for ***Tableau*** agents are the same as the ones set in **L7**, as well as the number of hidden nodes, the replay memory, and the batch size for ***ANN*** agents. However, we replaced the reward functions with the ones described in this section. Another modification is to consider *Result(tc,c) = 1* if the test $tc$ was not executed in the cycle *c*, as it was specified by T. Shi et al. (2020). 
The proposed rewards are based on the ***TCFail*** reward from **L7**. Thus, only the top 40\% tests will receive the reward value, while the remaining tests will be rewarded with zero. 
This allows us to evaluate the prioritization order. The settings for each **L8** variant are detailed in the following table:

> <img width="450" alt="image" src="https://github.com/user-attachments/assets/c3d7275a-e536-4fd2-831d-2f9e3b9eec28">

## L8 Variants
| Parameter | Type | Description | Specification |
| ------------- | ------------- | ------------- | ------------- |
| env_names | dictionary  | To name each environment | ``` env_names = {'dataset1': 'Dataset 1', 'dataset2': 'Dataset 2'} ``` |
| method_names | dictionary | To name each policy | ``` {'mlpclassifier': 'Network', 'tableau': 'Tableau', 'heur_random': 'Random', 'heur_sort': 'Sorting', 'heur_weight': 'Weighting'} ``` | 
| reward_names | dictionary | To name each reward | ``` {'rhe_whole_all': 'RHE whole all', 'rhe_whole_four': 'RHE whole four', 'rhe_part_all': 'RHE part all', 'rhe_part_four': 'RHE part four', 'the_whole_four': 'THE whole four', 'the_part_four': 'THE part four'} ``` |
| reward_funs | dictionary | Function to calcule each reward | ``` {'rhe_whole_all': rewards.Reward('rhe_whole_all'), 'rhe_whole_four': rewards.Reward('rhe_whole_four'), 'rhe_part_all': rewards.Reward('rhe_part_all'), 'rhe_part_four': rewards.Reward('rhe_part_four'), 'the_whole_four': rewards.Reward('the_whole_four'), 'the_part_four': rewards.Reward('the_part_four')} ``` |

## References:
- T. Shi, L. Xiao, and K. Wu, *"Reinforcement Learning Based Test Case Prioritization for Enhancing the Security of Software,"* 2020 IEEE 7th Int. Conf. on Data Science and Advanced Analytics (DSAA), Sydney, NSW, Australia, 2020, pp. 663-672, doi: 10.1109/DSAA49011.2020.00076.
ℹ️ [RL paper](https://ieeexplore.ieee.org/document/9260075)

- H. Spieker, A. Gotlieb, D. Marijan, and M. Mossige, *"Reinforcement learning for automatic test case prioritization and selection in continuous integration,"* 26th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2017), Santa Barbara, CA, USA, 2017, pp. 12-22, doi: 10.1145/3092703.3092709.
ℹ️ [RETECS paper](https://dl.acm.org/doi/10.1145/3092703.3092709)

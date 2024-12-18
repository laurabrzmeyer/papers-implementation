# L9 ALGORITHM

Welcome! This is the implementation of the **COLEMAN** method.

## Devellopers

- [ ] [Maria Laura BRZEZINSKI MEYER](https://github.com/laurabrzmeyer)

## Based on COLEMAN' original code

- Based on the version available in December 2022 (Realese 1.0)
- [ ] [COLEMAN](https://github.com/jacksonpradolima/coleman4hcs)

## COLEMAN Description

A well known reinforcement learning method is based on the concept of a slot machine, where after pulling the *arm* (i.e. doing an *action*), a *reward* is received (evaluative feedback). 
One can imagine *n* machines, that is, *n* different arms to pull. The challenge is to pull the arms that will return the biggest reward. 
This is called the *Multi-Armed Bandit* (***MAB***) problem. Therefore, there are two alternatives: try a random arm to discover what reward it will return (exploration) or pull the arms that already have given a good reward (exploitation). 
In the regression testing context, the arms are the test cases, and the action "to pull an arm" refers to the execution of a test. To deal with this *Exploration vs. Exploitation* (*EvE*) dilemma, several policies can be used. 
J. A. P. Lima et al. (2022) explore three policies: ***ε-greedy***, *Upper Confidence Bound* (***UCB***), and *Fitness-Rate-Rank Multi Armed Bandit* (***FRRMAB***).

The $\varepsilon$-greedy policy is the simplest one. An empirical quality estimator $\hat{q}$<sub>i,t</sub> is calculated using the sum of the previous rewards divided by the times the arm *i* has been pulled prior to time *t*. The arm with the highest $\hat{q}$<sub>i,t</sub> is chosen with a probability of $(1 - \varepsilon)$, i.e. an action is performed with exploitation. The exploration is done with a probability of $\varepsilon$, when it happens a random arm is chosen.

In the ***UCB*** policy, the same quality estimator $\hat{q}$<sub>i,t</sub> is used. But in this case, it is associated with the exploration term of the upper confidence bound. Therefore, the agent tends to explore when uncertainty is high, and as confidence increases, the algorithm will begin to exploit more. The *C* factor is introduced to avoid the scenario in which rewards normally fall within some range of real values that may disrupt the *EvE* balance.

*Fitness-Rate-Rank* is another ***UCB***-based ***MAB*** policy (K. Li et al. (2014)). It comprises two procedures: credit assignment and operator (arm/action) selection. The credit assignment is the procedure that teaches the policy about the actions according to past data. The quality estimator is replaced by a rank-based technique employing a *Fitness-Improvement-Rate* (*FIR*). The *FIR* values are stocked into a sliding window, then the reward of each arm can be calculated using the sum of these values. A rank can be assigned to each arm according to its reward. The rewards are corrected by a decaying factor, which is based on the relative position of an arm compared to other arms' rewards. Thus, the decay factor is normalized resulting in the *FRR* value. Finally, the operator selection is done: after all arms are chosen and evaluated, the next choices will follow the ***FRRMAB*** policy (according to the *FRR* value). 

Two reward functions are used. The first one is based on the result of the test, that is, *1* if the test fails and *0* otherwise. It is similar to ***TCFail*** from **L7**, it is designate as ***Reward Based on Failures*** (***RNFail***). The second is the ***Time-Ranked*** reward (***TRR***, the same as described for **L7**) and it verifies the rank of failing tests. If a test case that passes is ranked in the first position before the failing tests, the agent is penalized. The algorithm is available online. Further information regarding the **COLEMAN** method can be found in J. A. P. Lima (2021). The following table shows the 6 agents resulting from the combination of the three policies and the two rewards presented above.

> <img width="420" alt="image" src="https://github.com/user-attachments/assets/5bdbae2e-d8d9-4833-9cf5-9df3df854ae1">


## L9 Class
| Parameter | Type | Description | Specification |
| ------------- | ------------- | ------------- | ------------- |
| variant_name  | string  | Name of the variant | Predifined ones: L9.1.1, L9.1.2, L9.2.1, L9.2.2, L9.3.1, and L9.3.2 |
| win_size  | int  | Number of cycles to limit history | Default  is 20 | 
| INP  | input_data()  | To manage history data | Object from input_data class |
| policy_settings  | dictionary  | Dictionary to specify policy's parameters | EpsilonGreedy: ``` {'Type':'Egreedy', 'epsilon':float} ``` <br />  UCB: ``` {'Type':'UCB', 'C':float} ``` <br /> FRRMAB: ``` {'Type':'FRRMAB', 'C':float, 'DF':float} ``` |
| reward_type  | string  | String to specify reward type | Predifined ones: 'RBF' and 'TRR' |

## References:
- J. A. P. Lima and S. R. Vergilio, *"A Multi-Armed Bandit Approach for Test Case Prioritization in Continuous Integration Environments,"* IEEE Transactions on Software Engineering, vol. 48, no. 2, pp. 453-465, 1 Feb. 2022, doi: 10.1109/TSE.2020.2992428.
ℹ️ [COLEMAN paper](https://ieeexplore.ieee.org/document/9086053)

- K. Li, Á. Fialho, S. Kwong, and Q. Zhang, *"Adaptive Operator Selection With Bandits for a Multiobjective Evolutionary Algorithm Based on Decomposition,"* IEEE Transactions on Evolutionary Computation, vol. 18, no. 1, pp. 114-130, Feb. 2014, doi: 10.1109/TEVC.2013.2239648.
ℹ️ [FRRMAB paper](https://ieeexplore.ieee.org/document/6410018)

- J. A. P. Lima, *"A Multi-Armed Bandit Approach for Enhancing Test Case Prioritization in Continuous Integration Environments,"* [Doctoral dissertation, Federal University of Parana] Curitiba, PR, Brazil.
ℹ️ [J. A. P. Lima Doctoral Dissertation](https://acervodigital.ufpr.br/xmlui/handle/1884/73748})

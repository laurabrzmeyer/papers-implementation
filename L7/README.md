# L7 ALGORITHM

Welcome! This is the implementation of the **RETECS** method.

## Devellopers

- [ ] [Maria Laura BRZEZINSKI MEYER](https://github.com/laurabrzmeyer)

## Original code

- [ ] [RETECS](https://bitbucket.org/HelgeS/retecs/src/master/)

## RETECS Description

Reinforcement Learning is a technique that aims to learn by observing the changes in the environment after executing certain actions. 
So the algorithm receives a reward every time it makes a decision considered correct and is punished for erroneous actions. 
There are five main concepts in reinforcement learning: an *agent* that will learn in the process; a set of *actions*; an *environment* where the agent's actions will be performed; an environment *state* that will serve as input information for the agent; and a *reward* that will encourage or discourage the agent's decisions.

A reinforcement learning method named **RETECS** is introduced by H. Spieker et al. (2017) to prioritize tests. 
The code is available online. It corresponds to a model-free method, where there is no initial concept of the environment's dynamics. 
This method can be also considered as an online learning technique, as it is constantly learning during its runtime. 
Execution time, previous verdicts, and failure history are required for each test.

The set of test cases available at cycle *c* is defined as *T<sub>c</sub>*. The set of selected and scheduled tests by the **RETECS** algorithm is *TS<sub>i</sub>*, where *TS<sub>c</sub>* is a subset of *T<sub>c</sub>*. 
The subset of all failed test cases in *TS<sub>c</sub>* is noted as *TS<sub>fail</sub>(c)*. 

As mentioned in the paper, *"a policy is an approximated function from a state (a test case) to an action (a priority)"*. The authors, therefore, propose two policy models. 
The first one is the ***Tableau*** representation, which is composed of two tables. One table stores how many times an action was chosen and the other contains the average received reward for these actions. 
An ε-greedy strategy is used to balance the exploration and exploitation. The action with the highest reward for the current state is chosen with a probability of (1-ε). 
The second policy model uses Artificial Neural Network (***ANN***). The input of the ***ANN*** is a state and the output is an action. The exploration factor is based on a Gaussian distribution.

This method requires a feature named *LastResult* as input. It is a list of the previous results obtained by a test from the most recent to the oldest. 
In the absence of any indication from the authors as to how unexecuted tests should be treated, we considered the most recent executions and skipped the cycles with no verdict to create this feature. 
This approach is analogous to the strategy labeled *Case1* in **S3**. We have also done preliminary experiments with the *Case2* strategy, where the last cycles are taken into account. 
In this case, unexecuted tests are considered failed. But there was no performance improvement compared to the *Case1* strategy.

The consequence of the agents' action is a set of rewards, where each item corresponds to a specific test case. Three reward functions are defined to give feedback to agents after their actions. 
The first one is called *Failure Count Reward* (***FailCount***) and it aims to maximize the number of failed test cases. It is defined by the first equation below. 
The second one is the *Test Case Failure Reward* (***TCFail***) in the second equation. It returns the test case's verdict as a reward. 
In **L7**, the result of a failed test is recorded as zero, i.e. $Result(tc,c)=0* if *tc* failed in *c*. 
The third reward, *Time-Ranked Reward* (***TRR***), considers the order of each test case, as well as if it has failed. It can be calculated using the third equation below.

> 

To evaluate our first objective (decrease time for fault detection), we prioritize the tests, so all available tests (*T<sub>c</sub>*) will be present in *TS<sub>c</sub>*. 
It means that the reward ***FailCount*** will always be equal to the number of failed tests and ***TCFail*** will always be the test results. 
Since the ***TCFail** reward had the best performance for H. Spieker et al. (2017) and, knowing that its effect would be impacted because there is no selection of tests (only prioritization), we propose a modification. 
Both rewards are given only for the top 40\% tests of *TS<sub>c</sub>*. The reward is zero for the remaining tests. We carried out experiments to validate that this modification does not deteriorate the performance of ***RETECS***. 
The six variations resulting from the combination of agents (***Tableau*** and ***ANN***) and rewards (***FailCount***, ***TCFail*** and ***TRR***) are shown in the followngi table:

> 

- References:
    * H. Spieker, A. Gotlieb, D. Marijan, and M. Mossige, *"Reinforcement learning for automatic test case prioritization and selection in continuous integration,"* 26th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2017), Santa Barbara, CA, USA, 2017, pp. 12-22, doi: 10.1145/3092703.3092709.
    * [RETECS paper](https://dl.acm.org/doi/10.1145/3092703.3092709)
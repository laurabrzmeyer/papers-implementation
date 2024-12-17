[<img src="https://github.com/laurabrzmeyer/attachements/blob/main/article.png" height="40">]("add_targeting_to_the_article_latter") [<img src="https://github.com/laurabrzmeyer/attachements/blob/main/paper.png" height="40">](https://ieeexplore.ieee.org/document/10366626) [<img src="https://github.com/laurabrzmeyer/attachements/blob/main/library.png" height="40">](https://www.zotero.org/groups/5800690/rt_methods/library) [<img src="https://github.com/laurabrzmeyer/attachements/blob/main/contact.png" height="40">](mailto:laurabrzmeyer@gmail.com)

# RT Papers' Implementation

### Finding the right regression testing method: a taxonomy-based approach
This repository was created as a supplement to the article entitled *"Finding the right regression testing method: a taxonomy-based approach"*. We make our implementations available to help disseminate the methods proposed in the literature and to gather feedback from the scientific community on their interpretation.

#### Abstract
> The optimization of regression testing (RT) has been widely studied in the literature, and numerous methods exist. However, each context is unique. Therefore, a key challenge emerges: how to tell which method is more suitable for a specific industrial context? Recent work has proposed a taxonomy to help answer this question. By mapping both the RT problem and existing solutions onto the taxonomy, practitioners should be able to determine the solutions best aligned with their problem. Our work explores the practical relevance of this idea through an industrial case study.  The context is the development of R\&D projects at a major automotive company, in the domain of connected vehicles.  We developed an RT problem solving approach that uses the knowledge captured by the taxonomy. Following the approach, we characterized the RT problem and identified a set of 8 potentially relevant solutions from a set of 52 papers.   One of them stood out in the empirical evaluation, and could therefore be recommended to the industrial company. However, this success came at the cost of difficulties due to unclear taxonomy elements, missing ones, and  paper classification errors.  We conclude that the taxonomy would have to mature.

## Table of Contents
- [Contributors](#contributors)
- [Requirements](#requirements)
- [Dataset](#dataset)
- [Execution of Methods](#execution-of-methods)
- [Evaluation](#evaluation)

## Contributors
- :computer: Maria Laura Brzezinski Meyer
<a href="https://github.com/laurabrzmeyer/papers-implementation/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=laurabrzmeyer/papers-implementation" />
</a>

## Requirements
- [python](https://www.python.org/downloads/) $\geq$ 3.9
- [pandas](https://pandas.pydata.org/docs/index.html) 
- [numpy](https://numpy.org/)
- [matplotlib](https://matplotlib.org/)
- [seaborn](https://seaborn.pydata.org/)
- [plotly](https://plotly.com/)
- [tensorflow](https://www.tensorflow.org/) == 2.1.0 (for L4)
- [Keras](https://keras.io/) == 2.3.1 (for L4)
- [scikit-learn](https://scikit-learn.org/stable/) == 0.19.1 (for L7 and L8)
- [scipy](https://scipy.org/) == 1.4.1 (for L7 and L8)
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) (for L7 and L8)

## Dataset
Each row of the dataset used as input represents the execution of a test case for validation of a specific version of the SUT. We use a CSV file with semicolon (";") as a separator. Pandas will transform it into a dataframe. See below the description of each column:
| Columns | Type | Description | Specification |
| ------------- | ------------- | ------------- | ------------- |
| Cycle  | integer  | Number to order the SUT's versions | Used for experiments in ascending order |
| Version  | string  | The SUT's version | It is not mandatory | 
| Test  | string  | Test case identifier/name | Needs to be unique |
| Result  | string  | The result of the test's execution | Pass=0; Fail=1; NotExecuted=-1 |
| Duration | integer | Execution duration |  |
| RunDate | datetime | Date of execution | It can be a string (format='%Y-%m-%d %H:%M:%S') |
| Bugs | list of strings | List of bugs founded in the execution | It is mantory if the *Issue* scenario is used |

#### Columns for criteria of S22 used by us:
| Columns | Type | Description | Specification |
| ------------- | ------------- | ------------- | ------------- |
| FailProb  | float  | Probability of test failure | It is created by the script using 'Result' |
| ExecTime  | string  | The SUT's version | It is created by the script using 'Duration' | 
| ReqCov  | integer  | Number of requirements covered by the test | Need to be provided |
| TestCost | integer/float | Value to represent the test's cost | Need to be provided, we use the number of enablers required to execute the test |

#### Columns required by S26.2.* variants:
| Columns | Type | Description | Specification |
| ------------- | ------------- | ------------- | ------------- |
| StaticPrio  | float  | Static priority of the test | We use 3 levels of priority: 1, 2, and 3 |
| TestAge  | float  | The age of the test case | It can be calculated using the creation date of tests | 

#### Columns required by S34.2.* variants:
| Columns | Type | Description | Specification |
| ------------- | ------------- | ------------- | ------------- |
| Smoke  | boolean  | Used to distinguish the "smoke" tests subset | True or False |

#### Columns for L4 (managed by the function 'contruction_inputDL_asCases(data_path)'):
| Columns | Type | Description | Specification |
| ------------- | ------------- | ------------- | ------------- |
| Week  | datetime  | To separate runs into groups | It is created by the script using 'Cycle', but can be replaced by 'RunDate' |
| DurationFeature  | float  | It is the "Duration" normalized | It is created by the script using 'Duration' | 
| EX  | integer  | It is the "Result" of cycle c-X | It is created by the script using 'Result' (Pass=0;Fail=1;NotExecuted=-1) |
| EX_rocket  | integer  | It is the "Result" of cycle c-1 | It is created by the script using 'EX' (Pass=1;Fail=-1;NotExecuted=0) |
| LastRunFeature  | float  | It is the time since last execution | It is created by the script using 'Week' |
| DIST | integer | Distance from last fail | It is calculated by the script and can be 0 (if E1=1 and E2=E3=0), 1 (if E1=E3=0 and E2=1), or 2 (if E1=E2=0 and E3=1) |
| CHANGE_IN_STATUS  | integer  | Number of time the 'Result' changed | It is created by the script using 'EX' |
| PRIORITY_VALUE  | float  | It is the priority of a test according to ROCKET | It is created by the script using 'EX_rocket' |

#### Columns for L7/L8 (managed by the class 'IndustrialDatasetScenarioProvider'):
| Columns | Type | Description | Specification |
| ------------- | ------------- | ------------- | ------------- |
| ID  | integer  | An identifier unique for the run | - |
| CalcPrio  | float  | Priority of the test | Initialized as zero | 
| LastRun  | datetime  | It is the date of last execution | - |
| LR  | list of integers  | List of last results | It need to be ordered from the most to the last recent |

## Execution of Methods 

### Si

### Li

## Evaluation

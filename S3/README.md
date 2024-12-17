# S3 ALGORITHM

Welcome! This is the implementation of the **ROCKET** method.

## Devellopers

- [ ] [Maria Laura BRZEZINSKI MEYER](https://github.com/laurabrzmeyer)

## ROCKET Description

The **ROCKET** method is implemented in an industrial case study by D. Marijan et al. 
The authors validated **ROCKET** in the regression testing of a video conference system. 
The inputs required in this approach are as follows: a set of test cases to be prioritized, the test verdicts (i.e., "Pass" or "Fail") from previous executions, the test execution time, and the budget time allotted for testing. 
The priority is calculated based on the sum of past execution results weighted according to how recent the execution is. The equation below establishes the criteria for determining the weight of a past execution *i*:
    
> <img width="350" alt="image" src="https://github.com/user-attachments/assets/2afca2a5-a93c-454b-ba74-175322ece9cc">

The authors define test results as either *1* for "passed" executions or *-1* for "failed" ones. 
Accordingly, in our implementation of **S3**, *Result(tc, i)* values are set to *1* or *-1*. 
Therefore, the historical value (*HistValue*) of a test *tc* in a cycle *c* can be calculated as:
    
> <img width="300" alt="image" src="https://github.com/user-attachments/assets/4c10fd1a-ea43-4a1e-bfe2-171c0ffc2cc7">

    
However, execution time is also a crucial factor in test prioritization. 
Tests are first grouped by their *HistValue*, with each group assigned an integer label. 
The group with the lowest *HistValue* is labeled *1*, the next lowest is labeled *2*, and so on. 
Thus, if a test *tc* is situated within the third group, then *group(tc,c)=3*. 
Given a time budget *T<sub>max</sub>*, the execution time of each test *Te*, and the total number of groups *n*, the priority of a test can be calculated using the following equation:

> <img width="300" alt="image" src="https://github.com/user-attachments/assets/c7ffa9b3-d223-4fb5-9bac-3a80f3ca0e98">

It should be noted that the duration of the test has a direct impact on the final priority value, with longer execution times resulting in higher priority values. 
This approach entails ranking the test cases from the lowest to the highest priority.

For our datasets, the test execution time is not reliable, especially when executions are manual. 
In order to verify the influence of test execution time on the calculation of priorities, two variants were created: *WithTime* and *WithoutTime*. 
The first reflects the method described above, ordering the tests by $P(tc, c)$. 
The second one considers directly the result of *HistValue(tc,c)* as the priority of each test. 
In the latter case, if more than one test has the same value, the tiebreaker is random.

The data used in the original paper consists of five consecutive executions of a fixed test suite, so the scenario where a test was not executed is not addressed. 
To deal with this particularity present in our data, we created two solutions. 
In *Case1*, the results from the last executions are used, ignoring the cycles in which the test was not executed. 
For *Case2*, the only cycles considered are the last 3 ones, if the test was not executed *Result(tc,c)=0*. 

The following table shows the specifications of the four variants created by combining the different interpretations, i.e. *Case1 + withTime*, *Case1 + withoutTime*, *Case2 + withTime*, and *Case2 + withoutTime*.

> <img width="269" alt="image" src="https://github.com/user-attachments/assets/8b056797-b551-4176-9385-609f4de21cdd">

## S3 Class
| Parameter | Type | Description | Specification |
| ------------- | ------------- | ------------- | ------------- |
| variant_name  | string  | Name of the variant | Predifined ones: S3.1.1, S3.1.2, S3.2.1, and S3.2.2 |
| win_size  | int  | Number of cycles to limit history | Default  is 3 | 
| INP  | input_data()  | To manage history data | Object from input_data class |
| specification  | dictionary  | Dictionary to specify S3 parameters | {'weights':list of float, 'tmax':float} |

## References:
    * D. Marijan, A. Gotlieb and S. Sen, 
    *"Test Case Prioritization for Continuous Regression Testing: An Industrial Case Study,"*
    2013 IEEE International Conference on Software Maintenance, Eindhoven, Netherlands, 2013, pp. 540-543, 
    doi: 10.1109/ICSM.2013.91.
    * [ROCKET paper](https://ieeexplore.ieee.org/document/6676952)

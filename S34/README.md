# S34 ALGORITHM

Welcome! This is the implementation of the **MFF** and **ARM** methods.

## Devellopers

- [ ] [Maria Laura BRZEZINSKI MEYER](https://github.com/laurabrzmeyer)

## MFF/ARM Description

A method based on the Most Frequent Failures is introduced in J. Anderson et al. (2014), which we refer to as **MFF**. 
In this approach, every test case that has failed at least as many times as a predefined threshold is tagged as a test that will potentially fail again. 
The authors also present another method, which we denote as **ARM** (Association Rule Mining). Having a set of "smoke" tests, the aim is to select "regression" tests that are associated with this predefined set. 

Association rule mining is a popular method in data mining, used to discover interesting relationships or patterns among a set of items in a dataset. 
One key concept is the *support*, which measures the frequency of a collection of one or more items (*itemsets*) in the dataset. 
In this approach, the *support* of failed "smoke" tests (*ts*) is calculated (the following equation). These are a small subset of tests designed to quickly assess the overall health of the system. 
If a "smoke" test has a *support* higher than a predefined threshold, it is considered as significant.

> <img width="320" alt="image" src="https://github.com/user-attachments/assets/1c66793b-8401-4bfc-9957-ded29c87db13">

Another important concept is the *confidence*. It is the likelihood that an itemset *B* appears in transactions that contain another itemset *A*.
For us, it represents the frequency with which other tests (*tc*) have failed in the past when a significant "smoke" test *ts* has also failed (see the following equation).

> <img width="250" alt="image" src="https://github.com/user-attachments/assets/a45b0ed7-1b5f-4b47-8ec8-3b07336008f7">

The selected tests are those with a *confidence* higher than a predefined threshold.
For example, suppose the "smoke" test *ts<sub>10</sub>* has failed 6 times out of the last 9 runs.
If we set a $confidence$ threshold of *50\%*, then any test that failed at least 3 times out of those 6 would have a relevant association with *ts<sub>10</sub>*.
This means we consider it likely that these tests will fail again if *ts<sub>10</sub>* fails.

The set of "smoke" tests can be built in different ways. After questioning the authors, we were told that this test set was randomized for their study.
The authors also introduced the concept of window. The historical data considered can be all past executions or only the most recent ones. 
So for **S34**, we analyze four heuristic algorithms: *MFF<sub>Full</sub>*, *MFF<sub>Win</sub>*, *AMR<sub>Full</sub>*, *AMR<sub>Win</sub>*. They are listed in the table below:

> <img width="300" alt="image" src="https://github.com/user-attachments/assets/18a0f5af-afcd-43d7-8a90-9e4df2f1a6f2">

The original paper proposes a selection technique. Some tests are selected if frequently fail or if their association $confidence$ is above a threshold (set to *0.4* in the paper).
However, we are primarily interested in prioritizing the tests. To be able to compare **S34** with the other methods, the priority value of a test is determined by its failure rate (for **MFF** method) and association *confidence* (for **ARM** method). 

## S34 Class
| Parameter | Type | Description | Specification |
| ------------- | ------------- | ------------- | ------------- |
| variant_name  | string  | Name of the variant | Predifined ones: S34.1.1, S34.1.2, S34.2.1, and S34.2.2 |
| win_size  | int  | Number of cycles to limit history | Default  is 3 | 
| INP  | input_data()  | To manage history data | Object from input_data class |
| specification  | dictionary  | Dictionary to specify S34.2 parameters | ``` {'support':float} ``` |

## References:
- J. Anderson, S. Salem, and H. Do, *"Improving the effectiveness of test suite through mining historical data,"* 2014 11th Working Conf. on Mining Software Repositories (MSR), pp. 142–151, doi: 10.1145/2597073.2597084.
ℹ️ [MF/ARM paper](https://dl.acm.org/doi/10.1145/2597073.2597084)


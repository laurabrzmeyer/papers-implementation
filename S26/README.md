# S26 ALGORITHM

Welcome! This is the implementation of the **FAZ** and **EXTFAZ** methods.

## Devellopers

- [ ] [Maria Laura BRZEZINSKI MEYER](https://github.com/laurabrzmeyer)

## FAZ/EXTFAZ Description

In their proposition, E. Engström et al. (2011) investigate a method developed by Fazlalizadeh et al. (2009), calling it **FAZ** method. 
This approach uses three pieces of information to prioritize a test *tc* in a cycle *c*: historical effectiveness, execution history (*h(tc, c)*), and previous priority (*P<sub>Faz</sub>}(tc,c-1)*). 
Historical effectiveness represents the ratio of the number of times a test *tc* has failed before a cycle *c* (*f(tc,c)*) to the number of times it has been executed (*e(tc,c)*), also prior to *c*. 
The execution history increases by one each time the test is not executed. Three weighting parameters are defined: α, β, γ ∈ [0,1]. The priority *P<sub>Faz</sub>(tc,c)* can be defined as:

> <img width="300" alt="image" src="https://github.com/user-attachments/assets/ffcb2333-1371-4deb-baaa-9b067c3bf481">

Since there is no historical data to calculate the initial priority of a test (*P(tc,0)*), it is defined using the static priorities. 
The equation below defines the value assigned to a test *tc* according to their static priorities.

> <img width="300" alt="image" src="https://github.com/user-attachments/assets/7ab9fe65-18dc-40ca-8012-b06bc031f40f">
    
E. Engström et al. (2011) also improved the **FAZ** method, considering two other test case information in the prioritization calculation. 
The first is the test age relative to the current cycle. It is symbolized by *N(tc, c)* and defined in the equation: 

> <img width="300" alt="image" src="https://github.com/user-attachments/assets/1e54c1a8-e354-4e6c-aca5-5af5daaf9654">

The second information, introduced above, is the static priority *P(tc, 0)*. The incorporation of these two data gives rise to a method called **EXTFAZ**, in which priorities are calculated using the equation:

><img width="390" alt="image" src="https://github.com/user-attachments/assets/f48be720-749e-4300-b175-ad5baaf3a4dc">

We set the values of α, β, and γ as in the original paper: *0.04*, *0.7* and *0.7*, respectively. The size of the time window is not defined in either of the two studied articles. 
Therefore, both **FAZ** and **EXTFAZ** methods have 2 variants in our study: one where all past data is considered and another where this information is limited by a time window. 
    
The four methods are summarized in the table below:

> <img width="360" alt="image" src="https://github.com/user-attachments/assets/8a226393-1c90-47b2-af87-59b5792e91d6">

## S26 Class
| Parameter | Type | Description | Specification |
| ------------- | ------------- | ------------- | ------------- |
| variant_name  | string  | Name of the variant | Predifined ones: S26.1.1, S26.1.2, S26.2.1, and S26.2.2 |
| win_size  | int  | Number of cycles to limit history | Default  is 5 | 
| INP  | input_data()  | To manage history data | Object from input_data class |
| specification  | dictionary  | Dictionary to specify S26 parameters | ``` {'alpha':float, 'beta':float, 'gamma':float} ``` |

## References:
- E. Engström, P. Runeson, and A. Ljung, *"Improving Regression Testing Transparency and Efficiency with History-Based Prioritization -- An Industrial Case Study,"* 2011 Fourth IEEE International Conference on Software Testing, Verification and Validation, Berlin, Germany, 2011, pp. 367-376, doi: 10.1109/ICST.2011.27.
-  [EXTFAZ paper](https://ieeexplore.ieee.org/document/5770626)
  
-  Y. Fazlalizadeh, A. Khalilian, M. Azgomi and S. Parsa, *"Prioritizing test cases for resource constraint environments using historical test case performance data",*  2009 2nd IEEE International Conference on Computer Science and Information Technology, pp. 190-195, 2009, doi: 10.1109/ICCSIT.2009.5234968.
-  [FAZ paper](https://ieeexplore.ieee.org/abstract/document/5234968)

# S22 ALGORITHM

Welcome! This is the implementation of the **TOPSIS** method.

## Devellopers

- [ ] [Maria Laura BRZEZINSKI MEYER](https://github.com/laurabrzmeyer)

## TOPSIS/FTOPSIS Description

The Technique for Order Preference by Similarity to Ideal Solution (**TOPSIS**) was first introduced in the *Multiple Attribute Decision Making* book (C.-L. Hwang and K. Yoon (1981)). 
It is a method for decision support when multiple conflict criteria are present. 
This technique enables to identify the alternative with the smallest geometric distance from the positive ideal solution (*PIS*) and the largest geometric distance from the negative ideal solution (*NIS*). 
Consequently, the alternatives can be ranked in accordance with their degree of similarity to *PIS* and dissimilarity to *NIS*.

The combination of the **TOPSIS** and fuzzy principles is done by S. Tahvili et al. (2016), therefore, the **FTOPSIS** method is implemented. 
In this approach, each test case is represented by a vector composed of the membership degree for four criteria: fault detection probability, time efficiency, cost, and requirement coverage. 
The fuzzy positive and negative ideal solutions are also vectors. The test case priority is then defined by the distance of its vector from the positive and negative vectors. 
Since the values for each criterion (fault detection probability, time efficiency, cost, and requirement coverage) were qualitative, the authors chose to use fuzzy numbers for their representation. 

However, in our case, it is possible to quantify each criterion directly. Therefore, we will employ the **TOPSIS** technique, rather than **FTOPSIS**, in the implementation of the approach suggested by S. Tahvili et al. (2016).
The fault detection probability (*c1*) is calculated as the number of times the test has failed divided by the number of times it has been executed in the previous versions. 
The time efficiency (*c2*) can be represented by the execution time of each test. For our manual executions, the execution time of the tests is not a reliable data point. 
Consequently, the *c2* criterion is included in one variation of the method and excluded in another. 
The cost (*c3*) is estimated using the number of items required to execute the test (items under test). 
The requirement coverage (*c4*) is the number of requirements linked to a test case. 
Therefore, we want to maximize two criteria (*c1* and *c4*), which are called *benefit* criteria, and minimize two others (*c2* and *c3*), called *cost* criteria. 

The **TOPSIS** method is executed following six prescribed steps. The two **S22** variations diverge solely in the second step (*weight*). These steps are described in greater detail above.

1. ***Construction of decision matrix*** - A decision matrix *D* represents the current version of the software. Each criterion is a column and each test case (alternative) is a row. So, the value *d<sub>ij</sub>* represents the value of test *i* for the criterion *j*. There are *m* criteria and *n* test cases. The matrix is represented below:
> <img width="200" alt="image" src="https://github.com/user-attachments/assets/781f2058-8773-40db-9622-a56da152dbdf">

2. ***Weighting of each criterion*** - Each value *d<sub>ij</sub>}* of the matrix is multiplied by the *weight* of criteria *j*, as following:
> <img width="100" alt="image" src="https://github.com/user-attachments/assets/c9325338-96dd-4bf1-b28c-148f5c56b342">

3. ***Normalization of matrix D*** - Each new value *d<sup>''</sup><sub>ij</sub>* of the matrix is calculated using the equation below:
> <img width="100" alt="image" src="https://github.com/user-attachments/assets/5c9728ca-e415-4fe3-b4b1-f0dbba0d2a3d">

4. ***Calculation of PIS and NIS*** - The best case (*d<sub>j</sub><sup>+</sup>* in the first equation) and the worst case (*d<sub>j</sub><sup>-</sup>* in the second equation) are determined for each criterion, according to its type: whether it is a *benefit* (to be maximized) or a *cost* (to be minimized). The *PIS* vector comprises all best cases, while the *NIS* vector includes all worst cases (showed in the third line).
> <img width="300" alt="image" src="https://github.com/user-attachments/assets/596e0ea7-b32d-4246-9e30-9cb0f8dba50f">

5. ***Calculating distances*** - The distance of a test vector *i* from the vectors *PIS* (*D<sub>i</sub><sup>+</sup>*) and *NIS* (*D<sub>i</sub><sup>-</sup>*) is obtained using the following equations:
> <img width="300" alt="image" src="https://github.com/user-attachments/assets/31c9ef1b-19aa-47c0-a259-ff89a3324a65">

6. ***Calculating the proximity coefficient*** - The proximity coefficient for each test *i* is defined by:
> <img width="100" alt="image" src="https://github.com/user-attachments/assets/a8c28cf9-3000-4976-a289-ca237c3c51f6">

The higher the proximity coefficient *CC_i*, the further the test case *i* is from the *NIS*, therefore, the better it is ranked.
As done in **ROCKET**, two variants are evaluated to verify the influence of test execution time. In the original paper, all four criteria (fault detection probability, time efficiency, cost, and requirement coverage) have the same weight: *weight<sub>c1</sub>} = weight<sub>c2</sub> = weight<sub>c3</sub> = weight<sub>c4</sub> = 1*. 
In **S22.1**, this equal weighting is applied. Since the test execution time is not precise in our datasets, this criterion is given a weight of zero (*weight<sub>c2</sub>=0*) in the **S22.2** variant, while the others are weighted equally (*weight<sub>c1</sub>} = weight<sub>c3</sub> = weight<sub>c4</sub> = 1*). 
The characteristics of the two **S22** varieties are summarized in the table below:

> <img width="300" alt="image" src="https://github.com/user-attachments/assets/d080b970-f990-4948-b5f0-8ab406db62b7">

## S22 Class
| Parameter | Type | Description | Specification |
| ------------- | ------------- | ------------- | ------------- |
| variant_name  | string  | Name of the variant | Predifined ones: S22.1, S22.2 |
| win_size  | int  | Number of cycles to limit history | Default  is 5 | 
| INP  | input_data()  | To manage history data | Object from input_data class |
| specification  | dictionary | Dictionary to specify S22 parameters | ``` {criteria_name:(criteria_benefit, criteria_weight)} ```, where *criteria_name* is a string, *criteria_benefit* is a boolean, and *criteria_weight* is a float |

## References:
- Y.-J. Lai, T.-Y. Liu, and C.-L. Hwang, *"TOPSIS for MODM,"* European Journal of Operational Research, Volume 76, Issue 3, 1994, Pages 486-500, ISSN 0377-2217, doi: 10.1016/0377-2217(94)90282-8.
ℹ️ [TOPSIS paper](https://www.sciencedirect.com/science/article/pii/0377221794902828)
      
- S. Tahvili, W. Afzal, M. Saadatmand, M. Bohlin, D. Sundmark, and S. Larsson (2016). *"Towards Earlier Fault Detection by Value-Driven Prioritization of Test Cases Using Fuzzy TOPSIS,"* Latifi, S. (eds) Information Technology: New Generations. Advances in Intelligent Systems and Computing, vol 448. Springer, doi: 10.1007/978-3-319-32467-8_65.
ℹ️ [FTOPSIS paper](https://doi.org/10.1007/978-3-319-32467-8_65)
      
- C.-L. Hwang and K. Yoon (1981). *"Multiple attribute decision making,"* Springer Berlin, Heidelberg, 1 edition.
ℹ️ [Book Multiple Attribute Decision Making](https://link.springer.com/book/10.1007/978-3-642-48318-9)
    
    

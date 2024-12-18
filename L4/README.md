# L4 ALGORITHM

Welcome! This is the implementation of the **DeepOrder** method.

## Devellopers

- [ ] [Maria Laura BRZEZINSKI MEYER](https://github.com/laurabrzmeyer)

## Original code

- [ ] [DeepOrder-ICSME21](https://github.com/T3AS/DeepOrder-ICSME21)

## DeepOrder Description

A. Sharif et al. (2021) used deep learning methods to resolve the Regression Testing problem. 
The authors identified a limitation in the **ROCKET** algorithm, as it faces scalability issues when the historical data increases. 
First, a deep learning model is trained to predict the priority of each test case. 
These priorities are previously calculated using the **ROCKET** method. 
The goal is to maximize the fault detection capability and the number of test executions within a given time budget. 

The code for this method is open source. We analyzed it to identify the input features for training the deep learning model. 
The following features are used: *E1*, *E2*, and *E3*, which are the three last execution verdicts of a test; *Duration* of the test execution; *LastRunFeature*, which is the absolute time when a test was last run; 
*DIST* that represents the distance between the two most recent executions of a test; and *ChangeInStatus*, representing the number of times a test status has changed (from "pass" to "fail" or vice-versa). 
The label is the *PriorityValue* previously calculated using the **ROCKET** method.

The architecture is composed of three hidden layers with 10, 20, and 15 neurons. Each one uses a linear bi-parameter function *h(x) = θ<sub>0</sub> + θ<sub>1</sub> x*, where *x* is the input from the previous layer and *θ<sub>0</sub>* and *θ<sub>1</sub>* are the weight parameters. 
The activation function used is *Mish* (D. Misra (2020)). *Gradient descent* (S. Ruder (2017)) is used to perform backpropagation. 
Mean Square Error (*MSE*) determines the loss of the network, so the gradient concerning each neuron's weight parameters can be identified using partial derivatives. 
Subsequently, the weight parameters within each hidden layer are refined until the full dataset has been analyzed.

In order to implement this approach, we need to create an input based on our datasets. We use the a pre-script to create the inputs before training the deep learning model. 
We sought guidance from the authors regarding our proposed changes and cautioned them against potential errors in the original script. Both the original and our proposed code are available for review in this GitHub repository. 
The final input is presented in the format illustrated as follows:

> <img width="450" alt="image" src="https://github.com/user-attachments/assets/279e5ebe-c0c4-4642-8813-0cafa0f6f146">

An important change is that we do not drop runs with less than three past results. To get a *PrioValue* for all tests, we adopted the same reasoning as for **S3** i.e. *Case1*, which takes into account the last executions, and *Case2*, which gets the last cycles even if the test was not executed in one of them. 
Thus, we present two variants: *L4.1* considering the three last executions (*Case1*); and *L4.2* (*Case2*).

> <img width="300" alt="image" src="https://github.com/user-attachments/assets/5dfc603b-06a1-42d3-b63f-491ba35f3117">

## L4 Class
| Parameter | Type | Description | Specification |
| ------------- | ------------- | ------------- | ------------- |
| variant_name  | string  | Name of the variant | Predifined ones: L4.1, and L4.2 |
| INP  | input_data()  | To manage history data | Object from input_data class |

## References:
- A. Sharif, D. Marijan, and M. Liaaen, *"DeepOrder: Deep Learning for Test Case Prioritization in Continuous Integration Testing,"* 2021 IEEE Int. Conf. on Software Maintenance and Evolution (ICSME), pp. 525–534.
ℹ️ [DeepOrder paper](https://arxiv.org/abs/2110.07443)
      
- D. Misra, *"Mish: A Self Regularized Non-Monotonic Activation Function,"* arXiv preprint arXiv:1908.08681, 2020.
ℹ️ [Mish paper](https://arxiv.org/abs/1908.08681)
    
- S. Ruder, *"An overview of gradient descent optimization algorithms,"* arXiv preprint arXiv:1609.04747, 2017.
ℹ️ [Gradient Descent paper](https://arxiv.org/abs/1609.04747)

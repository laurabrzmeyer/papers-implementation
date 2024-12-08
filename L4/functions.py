import pandas as pd
from statistics import mean, stdev
from matplotlib import pyplot as plt
import os
import keras.backend as K
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split as tts
import warnings
warnings.simplefilter(action='ignore')

def mish(inputs):
    return inputs * tf.nn.tanh(tf.nn.softplus(inputs))

def root_mean_squared_error(y_true, y_pred):
    return K.sqrt(K.mean(K.square(y_pred - y_true)))

def split_dataset(X, Y):
    # splitting dataset, 80% training and 20% testing
    X_train, X_test, y_train, y_test = tts(X, Y, test_size=0.2) 
    # Scaling both training and testing input data.
    data_scaler = MinMaxScaler()
    X_train = data_scaler.fit_transform(X_train)
    X_test = data_scaler.transform(X_test)
    return X_train, X_test, y_train, y_test

def soft_acc(y_true, y_pred):
    return K.mean(K.equal(K.round(y_true), K.round(y_pred)))


# ### Defining function to plot correlation between loss and epochs

def loss_function(information):

    history_dict=information.history
    loss_values = history_dict['loss']
    val_loss_values=history_dict['val_loss']
    plt.plot(loss_values,'b--',label='training loss') # Training data loss
    plt.plot(val_loss_values,'r',label='training loss val') # Validation data loss
    plt.xlabel('Epochs',fontsize=22)
    plt.ylabel('Loss',fontsize=22)
    plt.title('Loss Curve',fontsize=22)
    save_figures(plt, 'loss_function_ccs')
    plt.close()

# ###  Defining function to plot the comparision between 'Actual' and 'Predicted' value.

def actual_vs_prediction(y_test, y_test_pred):

    outcome = pd.DataFrame({'Actual': y_test,'Predicted': y_test_pred.flatten()})
    df_sorted = outcome.head(40).sort_values(by="Actual")

    df_sorted.plot(kind='bar', figsize=(12,7))
    plt.grid(which='major', linestyle='-', linewidth = '0.5', color='green')
    plt.grid(which='minor', linestyle=':', linewidth = '0.5', color='black')
    plt.xlabel('Test Cases',fontsize=22)
    plt.ylabel('Priority Values',fontsize=22)
    plt.title("Comparision between 'Actual' and 'Predicted' values",fontsize=22)
    save_figures(plt, 'actual_vs_prediction_ccs')
    plt.close()

    plt.plot(df_sorted['Actual'].tolist(), label='Actual')
    plt.plot(df_sorted['Predicted'].tolist(), label='prediction')
    plt.xlabel('Test cases',fontsize=22)
    plt.ylabel('Priority Values',fontsize=22)
    plt.title("Comparision between 'Actual' and 'Predicted' values",fontsize=22)
    plt.grid(which='major', linestyle='-', linewidth = '0.5', color='green')
    plt.grid(which='minor', linestyle=':', linewidth = '0.5', color='black')
    plt.legend()
    save_figures(plt, 'actual_vs_prediction_2_ccs')
    plt.close()

# ###  Defining function to test the model

def prediction_function(X_train,X_test, model):
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    return y_test_pred

def save_figures(fig, filename):
    FIGURE_DIR = os.path.abspath(os.getcwd())
    fig.savefig(os.path.join(FIGURE_DIR+'/Results', filename + '.pdf'), bbox_inches='tight')


# ###  Defining function to plot the regression line for the model

def regression_line(y_test, y_test_pred):
    fig, ax = plt.subplots()
    ax.scatter(y_test, y_test_pred)
    ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=4)
    ax.set_xlabel('Calculated by DeepOrder algorithm',fontsize=22)
    ax.set_ylabel('Predicted by Neural Network',fontsize=22)
    plt.title("Neural Network Regression Line",fontsize=22)
    plt.grid(which='major', linestyle='-', linewidth = '0.5', color='green')
    plt.grid(which='minor', linestyle=':', linewidth = '0.5', color='black')
    save_figures(plt, 'regression_line_ccs')
    plt.close()

def create_model(df):
    
    #config = tf.compat.v1.ConfigProto()
    #config.gpu_options.allow_growth = True
    #session = tf.compat.v1.Session(graph=tf.compat.v1.get_default_graph(), config=config)
    X = df[['DurationFeature', 'E1','E2','E3', 'LastRunFeature','DIST','CHANGE_IN_STATUS']] # Defining feature variable
    Y = df['PRIORITY_VALUE'] # Defining label variable
    #MSE_list = [] # mean square error list
    #R2_list=[]  

    # ### Deep Neural Network 
                
    X_train, X_test, y_train, y_test = split_dataset(X, Y)
    model = Sequential()
    model.add(Dense(10, input_shape=(7,), activation=mish))
    model.add(Dense(20, activation=mish))
    model.add(Dense(15, activation=mish))
    model.add(Dense(1,))
    model.compile(Adam(lr=0.001), loss='mean_squared_error', metrics=[soft_acc])

    information = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs = 1000, 
                            validation_split = 0.2, shuffle = True, verbose = 0)

    '''
    y_test_pred = prediction_function(X_train, X_test, model)    
    MSE_list.append(mean_squared_error(y_test, y_test_pred))
    R2_list.append(r2_score(y_test, y_test_pred))       
    print('Average Mean Squared Error: %.6f'% mean(MSE_list))
    if (len(MSE_list)>1):
        print('Standard Deviation of MSE: %.6f'% stdev(MSE_list))
    print('Average R2 Score: %.6f'% mean(R2_list))
    if (len(R2_list) >1):
        print('Standard Deviation of R2 Score: %.6f'% stdev(R2_list))
    '''

    return model
    
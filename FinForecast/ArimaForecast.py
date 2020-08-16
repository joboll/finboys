"""
Wrapper package to make ARIMA forcasting easier.
Similar to R autoARIMA, but finer grained and some transformation functions.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)
import seaborn as sns

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima_model import ARMA
from statsmodels.tsa.arima.model import ARIMA


def plot_corr_function(df):
    """
    Take a pandas series and plot Auto-correlation function and Partial Auto-correlation
    """
    fig, ax = plt.subplots(2, 1, figsize= [8, 6])
    
    _ = plot_acf(df, color= 'blue', ax= ax[0])
    _ = plot_pacf(df, color= 'blue', ax= ax[1])# _ = est un truc pour éviter d'imprimer 2x le même plot

def get_stationarity(timeseries, window_size= 12 ):
    """
    Take a pandas serie timeseries in to output key indicators of stationarity
    """    
    # rolling statistics
    rolling_mean = timeseries.rolling(window= window_size).mean()
    rolling_std = timeseries.rolling(window= window_size).std()

    # rolling statistics plot
    fig= plt.figure(figsize= (15, 4))
    original = plt.plot(timeseries, color='black', label='Original', alpha= 0.3)
    mean = plt.plot(rolling_mean, color='coral', label='Rolling Mean')
    std = plt.plot(rolling_std, color='teal', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show(block=False)
    
    print("Mean MinMax Delta:", rolling_mean.max() - rolling_mean.min())
    print("Std MinMax Delta:", rolling_std.max() - rolling_std.min())
    
    # Dickey–Fuller test:
    result = adfuller(timeseries)
    print('ADF Statistic: {}'.format(result[0]))
    print('p-value: {}'.format(result[1]))
    print('Critical Values:')
    for key, value in result[4].items():
        print('\t{}: {}'.format(key, value))

def tfrm_to_MinusMean(PdSeries, window_size= 12):
    """
    Transform a Pandas Series to stationary by data point's standard deviation 
    (by substracting value from a rolling mean (deviation from mean)).
    Returns a Pandas Series and DataFrame with 'window_size' rolling average series
    
    #See why here: (https://towardsdatascience.com/machine-learning-part-19-time-series-and-autoregressive-integrated-moving-average-model-arima-c1005347b0d7)
    """

    df_ravg = PdSeries.rolling(window_size).mean()
    df_minus_mean = PdSeries - df_ravg
    df_minus_mean.dropna(inplace=True)
    return df_minus_mean, df_ravg

def AIC(PdSeries, order= (1,0,1)):
    """
    Take a Pandas series and fit an ARMA model of order= 
    to return Akaike Information Criterion
    """

    # Fit the data to an AR(1) model and print AIC:
    mod_arima = ARIMA(PdSeries, order= order)
    res_arima = mod_arima.fit()
    print("The AIC for an ARIMA{} is: {:5.0f} ".format(order, res_arima.aic))
    return res_arima.aic

def aic_optimize(PdSeries, ar_max_range= 8, ma_max_range= 12):
    """
    Take Pandas series and print Akaike Information Criterion for every order in 
    a range of order, ar(0) to ar(ar_max_range) and ma(0) to ma(ma_max_range).
    Also return a list of all AIC values. 
    """
    ar_ls= np.arange(0, ar_max_range)
    ma_ls= np.arange(0, ma_max_range)
    aic_ls= []
    for i in ar_ls:
        for j in ma_ls:
            aic = AIC(PdSeries, order= (i, 0, j))
            aic
            aic_ls.append(aic)
    return aic_ls

def rolling_window(a, step):
    shape   = a.shape[:-1] + (a.shape[-1] - step + 1, step)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def rollwin_ARIMA(df, actual= ['Adj Close'], ARIMA_order= (1,0,1), window_size= 100):
    """
    Take a DataFrame and train an ARIMA model on a rolling window to get
    a one step prediction (one data point beyond the window).
    
    Returns a DataFrame to compare actual data 'actual' VS predicted
    """
    
    output_df = pd.DataFrame(df.iloc[window_size : :])
    
    # Créer une liste de np.arrays de valeurs n=100 d'une fenêtre roulante
    r = rolling_window(np.array(df), window_size)

    # Init d'une liste de prédictions
    pred_col = []

    for i in r:
        mod_arma_t = ARIMA(i, order= ARIMA_order)
        res_arma_t = mod_arma_t.fit()

        # Prédire 1 jour au-delà du dataset (One step prediction)
        pred_arma_t = res_arma_t.predict(end= len(i) + 1) 
        # Ajouter la prédiction à la liste
        pred_col.append(pred_arma_t[window_size]) 

    output_df['Prediction'] = pred_col[0:-1]
    output_df['Erreur'] = output_df[actual] - output_df['Prediction']
    
    return output_df

# Accuracy metrics
def forecast_accuracy(forecast, actual):
    mape = np.mean(np.abs(forecast - actual)/np.abs(actual))  # MAPE
    me = np.mean(forecast - actual)             # ME
    mae = np.mean(np.abs(forecast - actual))    # MAE
    mpe = np.mean((forecast - actual)/actual)   # MPE
    rmse = np.mean((forecast - actual)**2)**.5  # RMSE
    corr = np.corrcoef(forecast, actual)[0,1]   # corr
    mins = np.amin(np.hstack([forecast[:,None], 
                              actual[:,None]]), axis=1)
    maxs = np.amax(np.hstack([forecast[:,None], 
                              actual[:,None]]), axis=1)
    minmax = 1 - np.mean(mins/maxs)             # minmax
    return({'mape':mape, 'me':me, 'mae': mae, 
            'mpe': mpe, 'rmse':rmse, 
            'corr':corr, 'minmax':minmax})

def arima_forecast(array, ARIMA_order= (1,0,1), window_size= 100 ):

        mod_arma_t = ARIMA(array, order= ARIMA_order)
        res_arma_t = mod_arma_t.fit()

        # Prédire 1 jour au-delà du dataset (One step prediction)
        pred_arma_t = res_arma_t.predict(window_size + 1) 
        
        return pred_arma_t


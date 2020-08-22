from statsmodels.tsa.arima.model import ARIMA
import backtrader as bt
from __future__ import (absolute_import, division, print_function,unicode_literals)
from FinForecast import ArimaForecast as af

class Strat_1d(bt.Strategy):
   
    def __init__(self, ARIMA_order= (1,0,1), window_size= 100):
        
        rolling_window = self.dataclose[0:-1*(window_size)])
        self.arima_forcast = af.arima_forecast(rolling_window, ARIMA_order)

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint: # Add if statement to only log of printlog or doprint is True
            dt = dt or self.datas[0].datetime.date(0)
            print('{0},{1}'.format(dt.isoformat(),txt))
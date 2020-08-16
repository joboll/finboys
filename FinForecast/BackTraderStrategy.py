from statsmodels.tsa.arima.model import ARIMA
import backtrader as bt
from __future__ import (absolute_import, division, print_function,unicode_literals)
from FinForecast import ArimaForecast as af

class Strat_1d(bt.Strategy):
    self.arima_forcast = af.ari
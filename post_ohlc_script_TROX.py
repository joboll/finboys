from FinForecast import Share
from FinForecast import Historical_stock as hist
#import pandas as pd


ticker = 'TROX'

data = hist.get_ohlc_as_tuple(ticker)
Share.by_ggsheet(data, 
                '1fj0fJu8DEYuLXNiefXLWOqExtEQZjX5I4eMhHGz-jJI', 
                'TROX_data')


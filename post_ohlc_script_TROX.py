from FinForecast import Share
#import pandas as pd


ticker = 'TROX'
#path_to_df_historical = '~/Documents/finboys/_Output/TROX_2020_pour_input_arima.pickle'
#df_historical = pd.read_pickle(path_to_df_historical)

#pred = Share.ARIMA_prediction(ticker, df_historical, path_to_df_historical, ARIMA_order= (2,0,5))

#subject = 'Prediction du jour'
#message = "Le modele predit que {} cloturera a {:.2f} USD le {}".format(ticker, pred, str(Share.infivedays()))
#destinataires = ['francoisroyca@gmail.com', 'victor.m.cerdacarvajal@gmail.com',' thomas.brown.05@gmail.com', 'finboys.news@gmail.com']

#Share.by_mail(subject, message, receiver_email=destinataires)

data = Share.ohlc_as_tuple(ticker)
Share.by_ggsheet(data, 
                '1fj0fJu8DEYuLXNiefXLWOqExtEQZjX5I4eMhHGz-jJI', 
                'TROX_data')


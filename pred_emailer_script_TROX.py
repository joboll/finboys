
from FinForecast import Share
import pandas as pd


ticker = 'TROX'
path_to_df_historical = '~/Documents/finboys/_Output/TROX_2020_pour_input_arima.pickle'
df_historical = pd.read_pickle(path_to_df_historical)

pred = Share.ARIMA_prediction(ticker, df_historical)

subject = 'Prediction du jour'
message = "Le modele predit que {} cloturera a {:.2f} USD le {}".format(ticker, pred, str(Share.infivedays()))
destinataires = ['francoisroyca@gmail.com', 'victor.m.cerdacarvajal@gmail.com',' thomas.brown.05@gmail.com', 'finboys.news@gmail.com']

Share.by_mail(subject, message, receiver_email=destinataires)

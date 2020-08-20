
from FinForecast import Share
import pandas as pd


ticker = 'TROX'
path_to_df_historical = '/Users/jonathanbeaulieu/Documents/PROG/FinBoys/_Output/TROX_2020_pour_input_arima.pickle'
df_historical = pd.read_pickle(path_to_df_historical)

pred = Share.get_pred(ticker, df_historical)

subject = 'Prediction du jour'
message = "Le modele predit que {} cloturera a {:.2f} USD le {}".format(ticker, pred, str(Share.infivedays()))
destinataires = ['finboys.news@gmail.com']
#['francoisroyca@gmail.com', 'victor.m.cerdacarvajal@gmail.com', 'finboys.news@gmail.com']

Share.emailer(subject, message, receiver_email=destinataires)
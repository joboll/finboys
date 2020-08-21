from yahoofinancials import YahooFinancials
import pandas as pd
import smtplib, ssl
from datetime import date, timedelta
from FinForecast import ArimaForecast as af


ticker = 'TROX'

# Init script to grab historical data base.
"""
    yahoo_financials = YahooFinancials(ticker)
    data = yahoo_financials.get_historical_price_data(start_date='2020-03-17',  
                                                    end_date='2020-08-19',  
                                                    time_interval='daily') 

    df_historical = pd.DataFrame(data[ticker]['prices'])
    col = list(df_historical.columns)
    col[-1] = 'Date'
    df_historical.columns = col
    df_historical = df_historical.drop('date', axis=1).set_index('Date')
    df_historical = df_historical.drop(columns=['high', 'low', 'open', 'volume', 'adjclose'])
    df_historical['rtn5'] = df_historical['close'].pct_change(5) * 100
    df_historical['meanDev'], df_ravg = af.tfrm_to_MinusMean(df_historical['rtn5'])
    df_historical.dropna(inplace=True)

    df_historical.to_pickle('_Output/TROX_2020_pour_input_arima.pkl')
    """

##################################################################################

def today():
    today = date.today()
    return today

def tomorrow(today= today()):
    delay = timedelta(days=1)
    tomorrow = today + delay
    return tomorrow

def infivedays(today= today(), delay= timedelta(days=5)):
    date_infivedays = today + delay
    return date_infivedays

def ARIMA_prediction(ticker, df_historical, ARIMA_order= (3,0,6), window_size=92):
    """
    Take a dataframe of the historical data of a stock to return ARIMA price forcast in 5 days.
    """

    # Get today's close price
    yahoo_financials = YahooFinancials(ticker)
    data_today = yahoo_financials.get_historical_price_data(start_date= str(today()),  
                                                    end_date=str(tomorrow()),  
                                                    time_interval='daily') 

    # Extracting the data out of the dictionnary
    date = [data_today[ticker]['prices'][-1]['formatted_date']]
    close = [data_today[ticker]['prices'][-1]['close']]

    # Create today's df with today's data
    df_today = pd.DataFrame(data= close, index= date, columns= ['close'])

    # Add today's data to historical data
    #df_historical = pd.read_pickle(path_to_df_historical)
    df_historical = df_historical.append(df_today)

    # Calcul today's return with 5 days ago
    todays_close = df_historical['close'].iloc[-1]
    five_days_ago_close = df_historical['close'].iloc[-6]
    todays_return5 = ( ( todays_close / five_days_ago_close ) - 1) * 100 
    df_historical['rtn5'].iloc[-1] = todays_return5

    # Transform (find) today's mean deviation return
    todays_transformed_return = todays_return5 - df_historical.iloc[-12:, 1].mean()
    df_historical['meanDev'].iloc[-1] = todays_transformed_return

    # Forcast (transformed return format)
    transformed_forecast = af.arima_forecast(df_historical['meanDev'], ARIMA_order= ARIMA_order, window_size= window_size)

    # Reverting the transformation to get closing price in 5 days
    erreur = todays_transformed_return - transformed_forecast
    pred_rtn5 = todays_return5 - erreur
    predicted_price_in_five_days = todays_close + (todays_close * (pred_rtn5 / 100))

    # Save the new df_historical
    #df_historical.to_pickle(path_to_df_historical)

    return predicted_price_in_five_days.iloc[0]


def by_mail(subject, message, sender_email= 'finboys.news@gmail.com', receiver_email=  'finboys.news@gmail.com', smtp_ssl= "smtp.gmail.com"):
    """
    Send a simple email to recipient through secure SSL.
    """
    
    port = 465  # For SSL
    password = "job211212"
    sender_email = sender_email
    receiver_email = receiver_email
    message = """\
    Subject: {subject}

    {message}""".format(subject= subject, message= message)

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_ssl, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)



from __future__ import print_function
from yahoofinancials import YahooFinancials
import pandas as pd
import smtplib, ssl
from datetime import date, timedelta
from FinForecast import ArimaForecast as af
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pprint import pprint
from googleapiclient import discovery


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

def infivedays(today= today(), delay= timedelta(days=7)):
    date_infivedays = today + delay
    return date_infivedays

def get_todays_close(ticker):
    """Returns a simple dataframe of today's date as index and ticker's close as value.
    Parameter:
        ticker (str): Official stock market ticker. Ex.: 'TROX'
    Exemple:
                    close
        2020-09-04   9.27
    """
    # Get today's close price
    yahoo_financials = YahooFinancials(ticker)
    data_today = yahoo_financials.get_historical_price_data(start_date= str(today()),  
                                                            end_date= str(tomorrow()),  
                                                            time_interval='daily') 

    # Extracting the data out of the dictionnary
    date = [data_today[ticker]['prices'][-1]['formatted_date']]
    close = [data_today[ticker]['prices'][-1]['close']]

    # Create today's df with today's data
    df_today = pd.DataFrame(data= close, index= date, columns= ['close'])

    return df_today

def ARIMA_prediction(df_today, df_historical, path_to_df_historical, ARIMA_order= (3,0,6), window_size=92):
    """
    Take a dataframe of the historical data of a stock to return ARIMA price foretcast in 5 days.
    """

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

    
def ohlc_as_tuple(ticker, start_date= '2020-01-01', end_date= str(tomorrow())):
    
    yahoo_financials = YahooFinancials(ticker)
    data_today = yahoo_financials.get_historical_price_data(start_date= start_date,  
                                                            end_date= end_date,  
                                                            time_interval= 'daily') 

    date = [ i['formatted_date'] for i in data_today[ticker]['prices']]
    high = [ i['high'] for i in data_today[ticker]['prices']]
    low = [ i['low'] for i in data_today[ticker]['prices']] 
    open_ = [ i['open'] for i in data_today[ticker]['prices']]
    close_ = [ i['close'] for i in data_today[ticker]['prices']]
    volume = [ i['volume'] for i in data_today[ticker]['prices']]
    adjclose = [ i['adjclose'] for i in data_today[ticker]['prices']]

    ohlc_tuple =  tuple(zip(date, high, low, open_, close_, volume, adjclose))
    ohlc_list = [list(i) for i in ohlc_tuple]

    return ohlc_list


def by_ggsheet(values, file_id, range_, value_input_option= 'RAW', insert_data_option= 'OVERWRITE'):

    """
    Add (append) values to google spreadsheet.

    Parameters:
        values (list): list of values to append. https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values
        file_id (str): Spreadsheet URL between d/ ... /edit
        range_: A1 notation of the range of field to apply append method. Will be first empty row of 
            column A anyway because it's what spreadsheets.values.append does.
    """

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('_Credentials/token.pickle'):
        with open('_Credentials/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '_Credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('_Credentials/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = discovery.build('sheets', 'v4', credentials=creds)

    # The ID of the spreadsheet to update.
    spreadsheet_id = file_id  


    value_range_body = {
    "range": range_,
    "majorDimension": 'ROWS',
    "values": values,
    }

    request = service.spreadsheets().values().append(spreadsheetId= file_id, 
                                                    range= range_, 
                                                    valueInputOption= value_input_option, 
                                                    insertDataOption= insert_data_option, 
                                                    body= value_range_body
                                                    )
    response = request.execute()
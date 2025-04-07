from Alerts.models import Result,  Alert
from ..consumers import WebSocketConsumer
from django.conf import settings
import requests

secret_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjdlMWJiNGE4MDZmZjE2NTFlOWVkMTE3IiwiaWF0IjoxNzQzMjEwMzUyLCJleHAiOjMzMjQ3Njc0MzUyfQ.r7KyuvSkZsUb91rCTfqIUnRJC7lJzF-cV_Nf8tTle6c"
price_url = "https://api.taapi.io/price"

def GetRSIStrategy(ticker):
    api_key = settings.FMP_API_KEY
    print(f"{ticker.symbol} - RSI")
    # result_success = 0
    # result_total = 0
    i = 0
    i += 1
    risk_level = None
    ticker_price_5min = None
    rsi_list = []
    intervals = ['5min', '1hour', '4hour', '1day']
    for interval in intervals:
        try:
            response = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{interval}/{ticker}?type=rsi&period=14&apikey={api_key}')
            result = response.json()
            if result != []:
                rsi_list.append(result[0]['rsi'])
        except Exception as e:
            print({'error': e})
            return 'Unknown', 0, 0
        
    if len(rsi_list) == 4:
        params = {
            'secret': secret_key,
            'type': 'stocks',
            'symbol': ticker,
            'interval': interval
        } 
        if all(rsi >= 75 for rsi in rsi_list):
            risk_level = 'Bearish'
            response = requests.get(price_url, params=params)
            if response.status_code == 200:
                data = response.json() 
                price = data.get("value")
                return risk_level, price, rsi_list
            else:
                # Handle error when price request fails
                return risk_level, 0, rsi_list
        # Check if RSI values indicate a 'Bullish' market
        elif all(rsi < 30 for rsi in rsi_list):
            risk_level = 'Bullish'
            response = requests.get(price_url, params=params)
            if response.status_code == 200:
                data = response.json() 
                price = data.get("value")
                return risk_level, price, rsi_list
            else:
                # Handle error when price request fails
                return risk_level, 0, rsi_list
        # If neither Bearish nor Bullish, return a default tuple
        else:
            return 'Unknown', 0, 0
    else:
        return 'Unknown', 0, 0
    # data_5min = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker.symbol}?type=rsi&period=14&apikey={api_key}')
    # data_1hour = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/1day/{ticker.symbol}?type=rsi&period=14&apikey={api_key}')
    # data_4hour = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/4hour/{ticker.symbol}?type=rsi&period=14&apikey={api_key}')
    # data_1day = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/1day/{ticker.symbol}?type=rsi&period=14&apikey={api_key}')
    # result_5min = data_5min.json()
    # result_1hour = data_1hour.json()
    # result_4hour = data_4hour.json()
    # result_1day = data_1day.json()
    # if result_5min != [] and result_1day != [] and result_4hour != [] and result_1hour != []:
    #     try:
    #         rsi_value_5min = result_5min[0]['rsi']
    #         ticker_price_5min = result_5min[0]['close']

    #         rsi_value_1hour = result_1hour[0]['rsi']
    #         ticker_price_1hour = result_1hour[0]['close']

    #         rsi_value_4hour = result_4hour[0]['rsi']
    #         ticker_price_4hour = result_4hour[0]['close']

    #         rsi_value_1day = result_1day[0]['rsi']
    #         ticker_price_1day = result_1day[0]
    #         # previous_value = result[1]['rsi']
    #         # previous_price = result[1]['close']
    #     except Exception as e:
    #         print({'error': e})
        # # to calculate results of strategy success according to current price ##
        # if (
        #     (previous_value > 70 and previous_price > ticker_price) or 
        #     (previous_value < 30 and previous_price < ticker_price)
        # ):
        #     result_success += 1
        #     result_total += 1
        # else:
        #     result_total += 1
        # Creating the Alert object and sending it to the websocket
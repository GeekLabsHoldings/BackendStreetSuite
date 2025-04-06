from Alerts.models import Result,  Alert
from ..consumers import WebSocketConsumer
from django.conf import settings
import requests

def GetRSIStrategy(ticker, timespan):
    api_key = settings.FMP_API_KEY
    print(f"{ticker.symbol} - RSI")
    # result_success = 0
    # result_total = 0
    i = 0
    i += 1
    risk_level = None
    ticker_price_5min = None
    data_5min = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker.symbol}?type=rsi&period=14&apikey={api_key}')
    data_1hour = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/1day/{ticker.symbol}?type=rsi&period=14&apikey={api_key}')
    data_4hour = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/4hour/{ticker.symbol}?type=rsi&period=14&apikey={api_key}')
    data_1day = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/1day/{ticker.symbol}?type=rsi&period=14&apikey={api_key}')
    result_5min = data_5min.json()
    result_1hour = data_1hour.json()
    result_4hour = data_4hour.json()
    result_1day = data_1day.json()
    if result_5min != [] and result_1day != [] and result_4hour != [] and result_1hour != []:
        try:
            rsi_value_5min = result_5min[0]['rsi']
            ticker_price_5min = result_5min[0]['close']

            rsi_value_1hour = result_1hour[0]['rsi']
            ticker_price_1hour = result_1hour[0]['close']

            rsi_value_4hour = result_4hour[0]['rsi']
            ticker_price_4hour = result_4hour[0]['close']

            rsi_value_1day = result_1day[0]['rsi']
            ticker_price_1day = result_1day[0]
            # previous_value = result[1]['rsi']
            # previous_price = result[1]['close']
        except Exception as e:
            print({'error': e})
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
        if rsi_value_1day >= 75 and rsi_value_4hour >= 75 and rsi_value_1hour >= 75 and rsi_value_5min >= 75:
            risk_level = 'Bearish'
        elif rsi_value_1day < 30 and rsi_value_4hour < 30 and rsi_value_1hour < 30 and rsi_value_1hour < 30:
            risk_level = 'Bullish'
        else:
            risk_level = None
            return None
        if risk_level!= None:
            obj = {
                'strategy': 'RSI',
                'result_value': rsi_value_5min,
                'risk_level': risk_level,
                'ticker_price': ticker_price_5min
            }
            return obj
    else:
        return None
    ## calculate the total result of strategy ##
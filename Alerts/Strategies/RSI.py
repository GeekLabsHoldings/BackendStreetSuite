from Alerts.models import Result,  Alert
from ..consumers import WebSocketConsumer
from django.conf import settings
import requests

def GetRSIStrategy(ticker, timespan):
    api_key = settings.FMP_API_KEY
    print(f"{ticker.symbol} - RSI")
    result_success = 0
    result_total = 0
    i = 0
    i += 1
    risk_level = None
    ticker_price = None
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker.symbol}?type=rsi&period=14&apikey={api_key}')
    result = data.json()
    if result != []:
        try:
            rsi_value = result[0]['rsi']
            ticker_price = result[0]['close']
            previous_value = result[1]['rsi']
            previous_price = result[1]['close']
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
        if rsi_value > 70:
            risk_level = 'Bearish'
        elif rsi_value < 30:
            risk_level = 'Bullish'
        else:
            risk_level = None
            return None
        if risk_level!= None:
            obj = {
                'strategy': 'RSI',
                'result_value': rsi_value,
                'risk_level': risk_level,
                'ticker_price': ticker_price
            }
            return obj
    ## calculate the total result of strategy ##
from Alerts.models import Result,  Alert
from ..consumers import WebSocketConsumer
from django.conf import settings
import requests

secret_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjdlMWJiNGE4MDZmZjE2NTFlOWVkMTE3IiwiaWF0IjoxNzQzMjEwMzUyLCJleHAiOjMzMjQ3Njc0MzUyfQ.r7KyuvSkZsUb91rCTfqIUnRJC7lJzF-cV_Nf8tTle6c"
price_url = "https://api.taapi.io/price"

def GetRSIStrategy(ticker):
    api_key = settings.FMP_API_KEY
    # result_success = 0
    # result_total = 0
    i = 0
    i += 1
    risk_level = None
    rsi_list = []
    intervals = ['5min', '1hour', '4hour', '1day']
    for interval in intervals:
        try:
            response = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{interval}/{ticker}?type=rsi&period=14&apikey={api_key}')
            result = response.json()
            if result != []:
                print(result[0]['rsi'])
                rsi_list.append(result[0]['rsi'])
                close = result[0]['close']
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
        if all(rsi >= 70 for rsi in rsi_list):
            risk_level = 'Bearish'
            price = close
            return risk_level, price, rsi_list
        # Check if RSI values indicate a 'Bullish' market
        elif all(rsi < 30 for rsi in rsi_list):
            risk_level = 'Bullish'
            risk_level = 'Bearish'
            price = close
            return risk_level, price, rsi_list
        # If neither Bearish nor Bullish, return a default tuple
        else:
            return 'Unknown', 0, 0
    else:
        return 'Unknown', 0, 0

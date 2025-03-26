from django.conf import settings
import requests

base_url = "https://api.taapi.io/rsi"
secret_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjdlMWJiNGE4MDZmZjE2NTFlOWVkMTE3IiwiaWF0IjoxNzQyODQ2Nzk0LCJleHAiOjMzMjQ3MzEwNzk0fQ.mWd_09tfp1RV5K8S2S4Iv3FBUkjgg0W4nXpeoMQWHWU"

price_url = "https://api.taapi.io/price"
def fetch_rsi_data(stock):
    # Define the parameters for the API request
    rsi_list = []

    price_params = {
        'secret': secret_key,
        'type': 'stocks',
        'symbol': stock,
    }
    intervals = ['5m','1h', '4h', '1d']
  
    for interval in intervals:
        params = {
            'secret': secret_key,
            'type': 'stocks',
            'symbol': stock,
            'interval': interval
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
                data = response.json()
                rsi_value = data.get("value")
                rsi_list.append(rsi_value)
        else:
            return f"Error {response.status_code}: {response.text}"
    
    if (rsi_list[0] >= 75 and rsi_list[1] >= 75 
            and rsi_list[2] >= 75 and rsi_list[3] >= 75):
            risk_level = 'Bearish'
            response = requests.get(price_url, params=price_params)
            data = response.json() 
            price =  data.get("value")
            obj = {
                    'strategy': 'RSI',
                    'risk_level': risk_level,
                    'ticker_price': price 
                }
            rsi_list = None
            return obj
    elif (rsi_list[0] < 30 and rsi_list[1] < 30
          and rsi_list[2] < 30 and rsi_list[3] < 30):
            risk_level = 'Bullish'
            response = requests.get(price_url, params=price_params)
            data = response.json() 
            price =  data.get("value")
            rsi_list = None
            

            return {
                    'strategy': 'RSI',
                    'risk_level': risk_level,
                    'ticker_price': price 
                }
    else: 
         return None
    


import requests

base_url = "https://api.taapi.io/rsi"
secret_key = "your_secret_key"
price_url = "https://api.taapi.io/price"

def fetch_rsi_data(stock):
    # Define the parameters for the API request
    rsi_list = []

    price_params = {
        'secret': secret_key,
        'type': 'stocks',
        'symbol': stock,
    }
    intervals = ['5m', '1h', '4h', '1d']

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
            # If there's an error, return a default value
            return 'Unknown', 0, 0

    # Check if RSI values indicate a 'Bearish' market
    if all(rsi >= 75 for rsi in rsi_list):
        risk_level = 'Bearish'
        response = requests.get(price_url, params=price_params)
        if response.status_code == 200:
            data = response.json() 
            price = data.get("value")
            return risk_level, price, rsi_list[0]
        else:
            # Handle error when price request fails
            return 'Unknown', 0, 0

    # Check if RSI values indicate a 'Bullish' market
    elif all(rsi < 30 for rsi in rsi_list):
        risk_level = 'Bullish'
        response = requests.get(price_url, params=price_params)
        if response.status_code == 200:
            data = response.json() 
            price = data.get("value")
            return risk_level, price, rsi_list[0]
        else:
            # Handle error when price request fails
            return 'Unknown', 0, 0
    
    # If neither Bearish nor Bullish, return a default tuple
    else:
        return 'Unknown', 0, 0

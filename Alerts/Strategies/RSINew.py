import requests

base_url = "https://api.taapi.io/rsi"
secret_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjdlMWJiNGE4MDZmZjE2NTFlOWVkMTE3IiwiaWF0IjoxNzQzMjEwMzUyLCJleHAiOjMzMjQ3Njc0MzUyfQ.r7KyuvSkZsUb91rCTfqIUnRJC7lJzF-cV_Nf8tTle6c"
price_url = "https://api.taapi.io/price"

def fetch_rsi_data(stock):
    # Define the parameters for the API request
    rsi_list = []


    intervals = ['5m', '1h', '4h', '1d']

    for interval in intervals:
        try :
            params = {
                'secret': secret_key,
                'type': 'stocks',
                'symbol': stock,
                'interval': interval
            }
            response = requests.get(base_url, params=params, timeout=4)
            if response.status_code == 200:
                data = response.json()
                rsi_value = data.get("value")
                print(rsi_value)
                rsi_list.append(rsi_value)
            else:
                print(f"Error: Received status code {response.status_code}")
                return 'Unknown', 0, 0 
        except Exception as e:
            print({'error': e})
            return 'Unknown', 0, 0
            

    # Check if RSI values indicate a 'Bearish' market
    if len(rsi_list) == 4: 
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

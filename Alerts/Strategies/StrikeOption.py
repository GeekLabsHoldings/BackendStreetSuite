from django.conf import settings
import requests
def GetStrike(ticker, timespan):
    print(f"{ticker.symbol} - strike")

    token = settings.UNUSUALWHALES_TOKEN 
    ## for Authentication on request ##
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'  # Optional, depending on the API requirements
    }
    response = requests.get(
        f'https://api.unusualwhales.com/api/stock/{ticker}/flow-per-strike-intraday', headers=headers).json()
    
    first_strike = response["data"][0]["strike"]
    
    obj = {
        "strategy": "Strike",
        "result_value": first_strike,
        "time_frame": timespan,
        "risk_level": None,
    }
    return obj if first_strike else None
    
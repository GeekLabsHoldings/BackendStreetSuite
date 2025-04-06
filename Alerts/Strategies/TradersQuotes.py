# from polygon import RESTClient
import requests
API_Key = "b4TSSpueZasKPSXaJzqcLtxtky5aHREh"

# https://api.polygon.io/v3/quotes/O:SPY241220P00720000?order=asc&limit=10&sort=timestamp&apiKey=b4TSSpueZasKPSXaJzqcLtxtky5aHREh
def GetTraderQuotes(ticker, future_date, risk, price):
    print(f"O:{ticker}{future_date}{risk}00{price}")
    ticker=f"O:{ticker}{future_date}{risk}00{price}000"
    response = requests.get(f'https://api.polygon.io/v3/quotes/{ticker}?order=asc&limit=1&sort=timestamp&apiKey={API_Key}')
    try:
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            bid_price = data["results"][0]["bid_price"]
            return bid_price
        else:
            return 0
    except Exception as e:
        print(f"Error in polygon.io: {e}")
        return 0
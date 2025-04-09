# from polygon import RESTClient
import requests
API_Key = "b4TSSpueZasKPSXaJzqcLtxtky5aHREh"
contracts_url = "https://api.polygon.io/v3/reference/options/contracts"

# https://api.polygon.io/v3/quotes/O:SPY241220P00720000?order=asc&limit=10&sort=timestamp&apiKey=b4TSSpueZasKPSXaJzqcLtxtky5aHREh
# https://api.polygon.io/v3/reference/options/contracts?underlying_ticker=SRPT&contract_type=call&expiration_date=2025-05-09&strike_price=48&order=asc&limit=10&sort=ticker&apiKey=b4TSSpueZasKPSXaJzqcLtxtky5aHREh
def GetTraderQuotes(ticker, future_date, risk, price):
    try:
        params = {
            'underlying_ticker': ticker,
            'contract_type': risk,
            'expiration_date': future_date,
            'strike_price': price,
            'order': 'asc',
            'limit': 1,
            'sort': 'ticker',
            'apiKey': API_Key
        }
        response = requests.get(contracts_url, params=params, timeout=4)
        data = response.json()
        option_results = data.get("results", [])
        option_ticker = option_results[0].get("ticker")
        print(option_ticker)
        response = requests.get(f'https://api.polygon.io/v3/quotes/{option_ticker}?order=asc&limit=1&sort=timestamp&apiKey={API_Key}').json()

        if "results" in response and len(response["results"]) > 0:
            bid_price = response["results"][0]["bid_price"]
            return bid_price
        else:
            return 0
    except Exception as e:
        print(f"Error in polygon.io: {e}")
        return 0
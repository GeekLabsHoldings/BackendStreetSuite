import requests
from Alerts.models import Alert , Ticker
from ..consumers import WebSocketConsumer
from datetime import date as dt, timedelta
from django.conf import settings
from Alerts.Scraping.EarningsScraper import earning_scraping

def GetEarnings(duration):
    ## returned list ##
    returned_list = {}
    # value = redis_client.get('tickers')
    api_key = settings.FMP_API_KEY
    ## token for request on current IV ##
    token = settings.UNUSUALWHALES_TOKEN 
    ## today date ##
    today = dt.today()
    print(today)
    ## date after period time ##
    thatday = today + timedelta(days=duration) 
    ## for Authentication on request for current IV ##
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json' 
    }
    ## response of the api ##
    response = requests.get(f'https://financialmodelingprep.com/api/v3/earning_calendar?from={thatday}&to={thatday}&apikey={api_key}')
    # print("response",response.json())
    if response.json() != []:
        for slice in response.json():
            Estimated_EPS = slice['epsEstimated']
            dotted_ticker = '.' in slice['symbol']
            if not dotted_ticker:
                if Estimated_EPS != None :
                    symbol = slice['symbol']
                    print("ticker: ",symbol)
                    print("Estimated_EPS: ",Estimated_EPS)
                    try:
                        try :
                            ticker = Ticker.objects.get(symbol=symbol)
                        except:
                            print("ticker not in our data base")
                            continue
                        time = slice['time']
                        print(f'time:{time}')
                        Estimated_Revenue = slice['revenueEstimated']
                        print(f"Estimated_Revenue : {Estimated_Revenue}")
                        if Estimated_Revenue != None:
                            Expected_Moves = earning_scraping(ticker.symbol)
                            print(f'Expected Moves:{Expected_Moves}')
                            if Expected_Moves != None:
                                current_IV = requests.get(f'https://api.unusualwhales.com/api/stock/{symbol}/option-contracts',headers=headers).json()['data'][0]['implied_volatility']
                                print(f'current_IV:{current_IV}')
                                alert = Alert.objects.create(ticker=ticker ,strategy= 'Earning', 
                                            time_frame = str(duration) , Estimated_Revenue = Estimated_Revenue, current_IV=current_IV,
                                            Estimated_EPS = Estimated_EPS , Expected_Moves=Expected_Moves , earning_time=time)
                                alert.save()
                                returned_list[ticker.symbol] = (Estimated_Revenue,None)
                                print(f"new alert for earning created for ticker {ticker.symbol}")
                                WebSocketConsumer.send_new_alert(alert)
                    except:
                        continue
    return returned_list


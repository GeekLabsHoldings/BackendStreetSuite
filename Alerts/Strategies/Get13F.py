import requests
from Alerts.models import Alert , Ticker
from datetime import datetime as dt
from ..consumers import WebSocketConsumer

def Get13F():
    list_of_CIK = ['0001067983']
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2' 
    day = str(dt.today().date())
    strategy = '13F strategy'
    for cik in list_of_CIK:      #https://financialmodelingprep.com/api/v4/institutional-ownership/portfolio-holdings?date=2024-10-1&cik=0001067983&page=0&apikey=juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2
        response = requests.get(f'https://financialmodelingprep.com/api/v4/institutional-ownership/portfolio-holdings?date={day}&cik={cik}&page=0&apikey={api_key}').json()
        if response != []:
            for slice in response:
                changeInSharesNumber = slice['changeInSharesNumber']
                name = slice['investorName']
                symbol = slice['symbol']
                ticker = Ticker.objects.get(symbol= symbol)
                if ticker != None:
                    ticker_data = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={api_key}').json()
                    price = ticker_data[0]['price']
                    amount_of_investment = float(price) * abs(changeInSharesNumber)
                    if amount_of_investment >= 1000000:
                        if changeInSharesNumber > 0 :
                            transaction = 'bought'
                        else:
                            transaction = 'sold'
                        try:
                            shares_quantity = abs(changeInSharesNumber)
                            alert = Alert.objects.create(investor_name = name , transaction_type = transaction , strategy=strategy,
                                                shares_quantity = shares_quantity , ticker= ticker ,
                                                ticker_price=price , amount_of_investment=amount_of_investment)
                            alert.save()
                            WebSocketConsumer.send_new_alert(alert)
                        except:
                            continue
        else:
            print("no transaction today")
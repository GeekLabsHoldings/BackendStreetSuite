import requests
from Alerts.models import Ticker , Result ,  Alert
from datetime import date as dt , datetime
from Alerts.consumers import WebSocketConsumer
from Alerts.Scraping.InsiderBuyerScraper import insider_buyers_scraper

## method to get data of ticker by api ##
def getIndicator(ticker , timespan , type):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type={type}&period=14&apikey={api_key}')
    return data.json()

def GetInsider_Buyer(*args, **kwargs):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    symbols = insider_buyers_scraper()
    tickers = Ticker.objects.filter(symbol__in=symbols)
    now = datetime.now()
    for ticker in tickers: 
        print(f'insider buyer {ticker.symbol}')
        response = requests.get(f'https://financialmodelingprep.com/api/v4/insider-trading?symbol={ticker.symbol}&page=0&apikey={api_key}').json()
        if response != []:
            for i in range(len(response)):
                filing_date_str = response[i]['filingDate']
                filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d %H:%M:%S")
                # checking if the date is within the range of the current date range
                if now.date() == filing_date.date():
                    # checking the transaction type if it is either sales or purchases if it is another type then pass 
                    if response[i]["transactionType"] == 'S-Sale'  or response[i]["transactionType"] == 'P-Purchase':
                        # the "price" means that each share of the common stock was sold or bought for this price and it is not comparable with the closed price.
                        print(f"alert in {ticker.symbol}")
                        try:
                            alert = Alert.objects.create(ticker=ticker, strategy='Insider Buyer', ticker_price=response[i]['price'],
                                        transaction_date=response[i]['transactionDate'], investor_name=response[i]['reportingName'],
                                        job_title=response[i]["typeOfOwner"], shares_quantity=response[i]["securitiesTransacted"],
                                        transaction_type=response[i]["transactionType"], filling_date=str(filing_date_str))
                            alert.save()
                            WebSocketConsumer.send_new_alert(alert)
                        except:
                            continue
                elif now.date() == filing_date:
                    result = getIndicator(ticker=ticker.symbol , timespan='1hour' , type='rsi')
                    price = result[0]['close']
                    old_price = result[1]['close']
                    ## calculating the strategy success result in selling and purchasing types  ##
                    # checking the transaction type if it is either sales or purchases if it is another type then pass# 
                    if response[i]["transactionType"] == 'S-Sale' or response[i]["transactionType"] == 'P-Purchase':
                        # comparing between the current close and the previous close
                        if (
                            (response[i]["transactionType"] == 'S-Sale' and price < old_price) or
                            (response[i]["transactionType"] == 'P-Purchase' and price > old_price)
                            ):
                            result = Result.objects.get(strategy='Insider Buyer')
                            result.success += 1
                            result.total += 1
                            result.result_value = (result.success / result.total)*100
                            result.save()
                        else:
                            result = Result.objects.get(strategy='Insider Buyer')
                            result.total += 1
                            result.result_value = (result.success / result.total)*100
                            result.save()
                        break
                else:
                    break
import requests
from Alerts.models import Ticker , Result ,  Alert
from datetime import date as dt , datetime
from celery import shared_task, chain
from .consumers import WebSocketConsumer
from django.core.cache import cache
############# import scraping ################
from .Scraping.TwitterScraper import twitter_scraper
from .Scraping.ShortIntrestScraper  import short_interest_scraper
from .Scraping.InsiderBuyerScraper import insider_buyers_scraper
################# import strategy #########################
from .Strategies.RSI import GetRSIStrategy
from .Strategies.EMA import GetEMAStrategy
from .Strategies.Earnings import GetEarnings
from .Strategies.MajorSupport import GetMajorSupport
from .Strategies.RelativeVolume import GetRelativeVolume
from .Strategies.insider_buyer import GetInsider_Buyer
from .Strategies.UnusualOptionBuys import GetUnusualOptionBuys
from .Strategies.Get13F import Get13F
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
# def get_tickers():
#     redis_client.set("tickers")

def get_cached_queryset():
    queryset = cache.get("tickerlist")
    if not queryset:
        queryset = Ticker.objects.all()
        cache.set("tickerlist", queryset, timeout=86400)
    return queryset

## method to get data of ticker by api ##
def getIndicator(ticker , timespan , type):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type={type}&period=14&apikey={api_key}')
    return data.json()

## tasks for MajorSupport strategy ##
# for time frame 1 day #
# @shared_task(queue='Main')
# def MajorSupport_1day():
#     GetMajorSupport(timespan='1day')

# # for time frame 4 hour #
# @shared_task(queue='celery_4hour')
# def MajorSupport_4hour():
#     GetMajorSupport(timespan='4hour')

# # for time frame 1 hour #
# @shared_task(queue='celery_1hour')
# def MajorSupport_1hour():
#     GetMajorSupport(timespan='1hour')

# ## endpint for RSI 4 hours ##
# @shared_task(queue='celery_4hour')
# def RSI_4hour():
#     GetRSIStrategy(timespan='4hour')
    
# ## endpint for RSI 1day ##
# @shared_task(queue='Main')
# def RSI_1day():
#     GetRSIStrategy(timespan='1day')



### relative volume ###
# @shared_task(queue='Main')
# def Relative_Volume():
#     all_tickers = get_cached_queryset()
#     for ticker in all_tickers:
#         GetRelativeVolume(ticker=ticker)

### task for 13F ###
# list_of_CIK = ['0001067983']
# @shared_task(queue='Main')
# def get_13f():
#     api_key_fmd = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2' 
#     day = str(dt.today().date())
#     strategy = '13F strategy'
#     for cik in list_of_CIK:
#         response = requests.get(f'https://financialmodelingprep.com/api/v4/institutional-ownership/portfolio-holdings?date={day}&cik={cik}&page=0&apikey={api_key_fmd}').json()
#         if response != []:
#             tickers = get_cached_queryset()
#             is_cached = True
#             previous_13F_alerts = cache.get(f"13F")
#             for slice in response:
#                 changeInSharesNumber = slice['changeInSharesNumber']
#                 name = slice['investorName']
#                 symbol = slice['symbol']
#                 ticker = next((ticker for ticker in tickers if ticker.symbol == symbol), None)
#                 if ticker != None:
#                     ticker_data = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={api_key_fmd}').json()
#                     price = ticker_data[0]['price']
#                     amount_of_investment = float(price) * abs(changeInSharesNumber)
#                     if amount_of_investment >= 1000000:
#                         if changeInSharesNumber > 0 :
#                             transaction = 'bought'
#                         else:
#                             transaction = 'sold'
#                         try:
#                             shares_quantity = abs(changeInSharesNumber)
#                             alert = Alert.objects.create(investor_name = name , transaction_type = transaction , strategy=strategy,
#                                                 shares_quantity = shares_quantity , ticker= ticker ,
#                                                 ticker_price=price , amount_of_investment=amount_of_investment)
#                             alert.save()
#                             WebSocketConsumer.send_new_alert(alert)
#                         except:
#                             continue

## Earning strategy in 15 days ##
# @shared_task(queue='Main')
# def earning15():
#     GetEarnings(duration=15)

# ## Earning strategy in 30 days ##
# @shared_task(queue='Main')
# def earning30():
#     GetEarnings(duration=30)



## task for Unusual Option Buys strategy ##
# @shared_task(queue='Main')
# def Unusual_Option_Buys(): 
#     all_tickers = get_cached_queryset()
#     for ticker in all_tickers:
#         GetUnusualOptionBuys(ticker=ticker)

# Insider Buyers Strategy
@shared_task(queue='celery_timeless')
def insiderBuyerTask(*args, **kwargs):
    GetInsider_Buyer()

# # Short Interest Strategy
@shared_task(queue="celery_timeless")
def Short_Interset_Task(*args, **kwargs):
    short_interest_scraper()

######## grouping tasks according to time frame ###########
## time frame 1 day ##
@shared_task(queue='celery_timeless')
def timeless_tasks():
    chain(insiderBuyerTask.s(), Short_Interset_Task.s())()

######## COMMON METHOD FOR COMMON ALERTS #########
def common(timeframe):
    print("start")
    all_tickers = get_cached_queryset()
    print("got tickers")
    if timeframe == '1hour':
        applied_functions = [GetEMAStrategy, GetMajorSupport]
    elif timeframe == '1day' :
        applied_functions = [GetRSIStrategy,GetEMAStrategy,GetMajorSupport,GetUnusualOptionBuys]
    else:
        applied_functions = [GetRSIStrategy,GetEMAStrategy,GetMajorSupport]
    for ticker in all_tickers:
        print(ticker.symbol)
        ## initialize list of alerts that common on the same ticker ##
        list_alerts = []
        ## initialize list of applied functions for the time frame ##
        for function in applied_functions:
            if function == GetEarnings:
                alert = function(duration=15)
            alert = function(ticker=ticker, timespan=timeframe)
            if alert != None:
                list_alerts.append(alert)
        ## check if the alerts came from the same ticker is more than 3 ##
        if len(list_alerts)>=2:
            print("more than 2")
            message = ''
            for alert in list_alerts:
                message += f'{alert.strategy}_{alert.result_value}_{alert.risk_level}/ '
            print(message)
            ## create common alert with the data of common alerts ###
            alert = Alert.objects.create(ticker=ticker ,strategy='Common Alert', investor_name=message ,time_frame=timeframe )
            alert.save()
            WebSocketConsumer.send_new_alert(alert)
    print("finsh")          
                  

@shared_task(queue='celery_1hour')
def tasks_1hour():
    common(timeframe='1hour')
            
@shared_task(queue='celery_4hour')
def tasks_4hour():
    common(timeframe='4hour')

@shared_task(queue='Main')
def tasks_1day():
    common(timeframe='1day')
            
@shared_task(queue="Twitter")
def twitter_scrap():
    twitter_scraper()

import requests
from Alerts.models import Ticker ,  Alert
from celery import shared_task, chain
from .consumers import WebSocketConsumer
from django.core.cache import cache
############# import scraping ################
from .Scraping.TwitterScraper import twitter_scraper
from .Scraping.ShortIntrestScraper  import short_interest_scraper
################# import strategies #########################
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

# Insider Buyers Strategy
@shared_task(queue='celery_timeless')
def insiderBuyerTask(*args, **kwargs):
    GetInsider_Buyer()

# # Short Interest Strategy
@shared_task(queue="celery_timeless")
def Short_Interset_Task(*args, **kwargs):
    short_interest_scraper()

# # Short Interest Strategy
@shared_task(queue="celery_timeless")
def Relative_volume(*args, **kwargs):
    GetRelativeVolume()

######## grouping tasks according to time frame ###########
## timeless tasks ##
@shared_task(queue='celery_timeless')
def timeless_tasks():
    chain(insiderBuyerTask.s(), Short_Interset_Task.s(),Relative_volume.s())()

######## COMMON METHOD FOR COMMON ALERTS #########
def common(timeframe,applied_functions,list_13f=None,list_earning15=None,list_earning30=None):
    all_tickers = get_cached_queryset()
    for ticker in all_tickers:
        print(ticker.symbol)
        ## initialize list of alerts that common on the same ticker ##
        list_alerts = []
        ## initialize list of applied functions for the time frame ##
        for function in applied_functions:
            alert = function(ticker=ticker, timespan=timeframe)
            if alert != None:
                list_alerts.append(alert)
            if timeframe == '1day':
                if ticker.symbol in list_13f.keys():
                    print("ticker in 13f list")
                    alert = Alert.objects.create(ticker=ticker,strategy='13f',result_value = list_13f[ticker.symbol][0], risk_level = list_13f[ticker.symbol][1])
                    list_alerts.append(alert)
                if ticker.symbol in list_earning15.keys():
                    print("ticker in earning15 list")
                    alert = Alert.objects.create(ticker=ticker,strategy='earning 15',result_value = list_earning15[ticker.symbol][0], risk_level = list_13f[ticker.symbol][1])
                    list_alerts.append(alert)
                if ticker.symbol in list_earning30.keys():
                    alert = Alert.objects.create(ticker=ticker,strategy='earning 30',result_value = list_earning30[ticker.symbol][0],risk_level = list_13f[ticker.symbol][1])
                    print("ticker in earning30 list")
                    list_alerts.append(alert)
        ## check if the alerts came from the same ticker is more than 3 ##
        if len(list_alerts)>=2:
            message = ''
            for alert in list_alerts:
                message += f'{alert.strategy}_{alert.result_value}_{alert.risk_level}/ '
            ## create common alert with the data of common alerts ###
            alert = Alert.objects.create(ticker=ticker ,strategy='Common Alert', investor_name=message ,time_frame=timeframe )
            alert.save()
            WebSocketConsumer.send_new_alert(alert)          
                  

@shared_task(queue='celery_1hour')
def tasks_1hour():
    common(timeframe='1hour',applied_functions=[GetEMAStrategy, GetMajorSupport])
            
@shared_task(queue='celery_4hour')
def tasks_4hour():
    common(timeframe='4hour',applied_functions=[GetRSIStrategy,GetEMAStrategy,GetMajorSupport])

@shared_task(queue='Main')
def tasks_1day():
    list_13f = Get13F()
    list_earning15 = GetEarnings(duration=15)
    list_earning30 = GetEarnings(duration=30)
    common(timeframe='1day',applied_functions=[GetRSIStrategy,GetEMAStrategy,GetMajorSupport,GetUnusualOptionBuys],
                                        list_13f=list_13f,list_earning15=list_earning15,list_earning30=list_earning30)
            
@shared_task(queue="Twitter")
def twitter_scrap():
    twitter_scraper()

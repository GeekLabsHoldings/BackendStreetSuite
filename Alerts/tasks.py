import requests
from Alerts.models import Ticker ,  Alert
from celery import shared_task, chain
from .consumers import WebSocketConsumer
from django.core.cache import cache
from datetime import datetime, timedelta
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
from .Strategies.StrikeOption import GetStrike
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
# def get_tickers():
#     redis_client.set("tickers")

def get_cached_queryset():
    queryset = cache.get("tickerlist")
    if not queryset:
        queryset = Ticker.objects.filter(market_capital__in=["Mega", "Large"])
        cache.set("tickerlist", queryset, timeout=86400)
    return queryset

## method to get data of ticker by api ##
def getIndicator(ticker , timespan , type):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type={type}&period=14&apikey={api_key}')
    return data.json()

# Insider Buyers Strategy
# @shared_task(queue='celery_timeless')
# def insiderBuyerTask(*args, **kwargs):
#     GetInsider_Buyer()

# # # Short Interest Strategy
# @shared_task(queue="celery_timeless")
# def Short_Interset_Task(*args, **kwargs):
#     short_interest_scraper()

# # # Short Interest Strategy
# @shared_task(queue="celery_timeless")
# def Relative_volume(*args, **kwargs):
#     GetRelativeVolume()

# ######## grouping tasks according to time frame ###########
# ## timeless tasks ##
# @shared_task(queue='celery_timeless')
# def timeless_tasks():
#     chain(insiderBuyerTask.s(), Short_Interset_Task.s(),Relative_volume.s())()

# ######## COMMON METHOD FOR COMMON ALERTS #########
def common(timeframe,applied_function):
    all_tickers = get_cached_queryset()
    for ticker in all_tickers:
        message = ''
        alert = applied_function(ticker, timeframe)
        if alert is not None:
            today = datetime.today().date()

            # Add 30 days
            future_date = today + timedelta(days=30)

            if alert['risk_level'] == 'Bearish':
                message = f'Option Type = Put Buy\nOption Strike = {alert['ticker_price']}\nOption Expiry = {future_date}' 
                   
            elif alert['risk_level'] == 'Bullish':
                message = f'Option Type = Call Buy\nOption Strike = {alert['ticker_price']}\nOption Expiry = {future_date}'

            alert = Alert.objects.create(ticker=ticker, strategy='New Alert',
                                         result_value=alert['result_value'],
                                        investor_name=message,
                                        risk_level=alert['risk_level'],
                                        time_frame=timeframe)
            alert.save()
            WebSocketConsumer.send_new_alert(alert)
        ## initialize list of alerts that common on the same ticker ##
        # list_alerts = []
        # ## initialize list of applied functions for the time frame ##
        # for function in applied_functions:
        #     alert = function(ticker=ticker, timespan=timeframe)
        #     if alert != None:
        #         list_alerts.append(alert)
        # if len(list_alerts) >= 1:
        #     message = ''
        #     for alert in list_alerts:
        #         message += f'{alert['strategy']} - {alert['result_value']} - {alert['risk_level']} / '
        #     ## create common alert with the data of common alerts ###
        #     alert = Alert.objects.create(ticker=ticker ,strategy='New Alert', investor_name=message ,time_frame=timeframe)
        #     alert.save()
        #     WebSocketConsumer.send_new_alert(alert)
                 
                  

@shared_task(queue='celery_5mins')
def tasks_5mins():
    # common(timeframe='5mins',applied_functions=[GetRSIStrategy])
    common(timeframe='5mins',applied_function=GetRSIStrategy)

# @shared_task(queue='celery_1hour')
# def tasks_1hour():
#     # common(timeframe='1hour',applied_functions=[GetRSIStrategy])
#     common(timeframe='1hour', applied_function=GetRSIStrategy)
            
# @shared_task(queue='celery_4hour')
# def tasks_4hour():
#     # common(timeframe='4hour',applied_functions=[GetRSIStrategy])
#     common(timeframe='4hour', applied_function=GetRSIStrategy)

# @shared_task(queue='celery_1day')
# def tasks_1day():
#     # common(timeframe='1day',applied_functions=[GetRSIStrategy])
#     common(timeframe='1day', applied_function=GetRSIStrategy)

# @shared_task(queue='Main')
# def tasks_1day():
#     list_13f = Get13F()
#     list_earning15 = GetEarnings(duration=15)
#     list_earning30 = GetEarnings(duration=30)
#     common(timeframe='1day',applied_functions=[GetRSIStrategy,GetEMAStrategy,GetMajorSupport,GetUnusualOptionBuys],
#                                         list_13f=list_13f,list_earning15=list_earning15,list_earning30=list_earning30)
            
# @shared_task(queue="Twitter")
# def twitter_scrap():
#     twitter_scraper()

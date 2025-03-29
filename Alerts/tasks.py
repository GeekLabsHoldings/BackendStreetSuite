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
from .Strategies.RSINew import fetch_rsi_data
from .Strategies.TradersQuotes import GetTraderQuotes


def get_cached_queryset():
    queryset_data = cache.get("tickerlist")
    
    if queryset_data is None or not isinstance(queryset_data, list):
        excluded_symbols = [
        "ACM", "AFG", "AFRM", "AGNCL", "AGNCM", "AGNCN", "AGNCO", "AGNCP", "AGR", "ALLY", "ALNY",
        "AMH", "APO", "APOS", "APP", "AQNB", "ARES", "ARMK", "ATR", "AVTR", "AZPN", "BJ", "BLD",
        "BMRN", "BSY", "BURL", "CAVA", "CCZ", "CET", "CG", "CHDN", "CHWY", "CLH", "CNA", "COHR",
        "COIN", "COKE", "CPNG", "CQP", "CRBG"
        ]
        queryset = (
        Ticker.objects
        .filter(market_capital__in=["Mega", "Large"])
        .exclude(symbol__in=excluded_symbols)
        .values("id", "symbol", "market_capital")
    )
        queryset_data = list(queryset)  
        cache.set("tickerlist", queryset_data, timeout=86400)  # Store only list of dictionaries

    return queryset_data 
## method to get data of ticker by api ##
def getIndicator(ticker , timespan , type):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type={type}&period=14&apikey={api_key}')
    return data.json()


# ######## COMMON METHOD FOR COMMON ALERTS #########
def common(timeframe,applied_function):
    all_tickers = get_cached_queryset()
    print("new loop")
    for ticker in all_tickers:
        message = ''
        print(ticker["symbol"])
        # alert = applied_function(ticker, timeframe)
        result = fetch_rsi_data(ticker["symbol"])
        
# Check if the result is valid before unpacking
        if result[0] != 'Unknown':
            risk_level, ticker_price, rsi_value = result
            today = datetime.today().date()
            print(risk_level)
            # Add 30 days
            future_date = today + timedelta(days=30)
            formatted_future_date = future_date.strftime("%y%m%d")
            ticker_price= int(ticker_price)
            if risk_level == 'Bearish':
                bid_price = GetTraderQuotes(ticker["symbol"], formatted_future_date,'P', ticker_price )
                # options = GetUnusualOptionBuys(ticker, future_date)
                message = f'Option Type = Put Buy\nOption Strike = {ticker_price}\nOption Expiry = {future_date}\n Entry price = {bid_price}'
                   
            elif risk_level == 'Bullish':
                bid_price = GetTraderQuotes(ticker["symbol"], formatted_future_date,'C', ticker_price )
                # options = GetUnusualOptionBuys(ticker, future_date)
                message = f'Option Type = Call Buy\nOption Strike = {ticker_price}\nOption Expiry = {future_date}\n Entry price = {bid_price}'
            alert = Alert.objects.create(ticker=ticker, strategy='New Alert',
                                         result_value=int(rsi_value),
                                        investor_name=message,
                                        risk_level=risk_level,
                                        )
            alert.save()
            print(f'alert{ticker["symbol"]}' )
            WebSocketConsumer.send_new_alert(alert)
                 
@shared_task(queue='celery_5mins')
def tasks_5mins():
    # common(timeframe='5mins',applied_functions=[GetRSIStrategy])
    common(timeframe='5mins',applied_function=GetRSIStrategy)



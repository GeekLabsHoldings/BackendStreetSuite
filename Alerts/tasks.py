from Alerts.models import Alerts_Details ,Tickers, Social_media_mentions
import requests
from datetime import date
from QuizApp.models import UserEmail
from celery import shared_task
from .TwitterScraper import main as scrape_twitter
from .RedditScraper import main as scrape_reddit
def getIndicator(ticker , timespan , type):
    print("abvsd")
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type={type}&period=14&apikey={api_key}')
    print(data.json())
    return data.json()

## rsi function ##
def rsi(timespan):
    strategy = f'RSI strategy per {timespan}'
    tickers = Tickers.objects.all()
    # data = []
    for ticker in tickers:
        risk_level = None
        result = getIndicator(ticker=ticker.title , timespan=timespan , type='rsi')
        rsi_value = result[0]['rsi']
        date = result[0]['date']
        if rsi_value > 70:
            risk_level = 'Overbought'
        if rsi_value < 30:
            risk_level = 'Underbought'
        message = f"Using rsi Strategy, The Ticker {ticker} , this Stock is {risk_level}, with rsi value = {rsi_value} in date {date} "
        if risk_level != None:
            Alerts_Details.objects.create(ticker=ticker.title , strategy= strategy , value = rsi_value , message = message)
            # return data

## ema function ##
def ema(timespan):
    strategy = f'EMA strategy per {timespan}'
    tickers = Tickers.objects.all()
    # data = []
    for ticker in tickers:
        result = getIndicator(ticker=ticker.title , timespan=timespan , type='ema')
        if result != []:
            risk_level = None
            ema_value = result[0]['ema']
            currunt_price = result[0]['close']
            old_price = result[1]['close']
            if ema_value < currunt_price and ema_value > old_price:
                risk_level = 'Bullish'
            if ema_value > currunt_price and ema_value < old_price:
                risk_level = 'Bearish'
            message = f"Using EMA Strategy, The Ticker {ticker} with Price {currunt_price}, and old price {old_price} this Stock is {risk_level}, with EMA value = {ema_value}"
            if risk_level != None:
                Alerts_Details.objects.create(ticker=ticker.title , strategy= strategy , value = ema_value ,risk_level=risk_level , message = message)
        # return data

## endpint for RSI 4 hours ##
@shared_task
def RSI_4hour():
    rsi(timespan='4hour')

## endpint for RSI 1day ##
@shared_task
def RSI_1day():
    rsi(timespan='1day')

## view for EMA  1day ##
@shared_task
def EMA_DAY():
    ema(timespan='1day')

## view for EMA  4hour ##
@shared_task
def EMA_4HOUR():
    print("aaaaaaaaaaaa")
    ema(timespan='4hour')

## view for EMA  1hour ##
@shared_task
def EMA_1HOUR():
    ema(timespan='1hour')

@shared_task
def web_scraping_alerts():
    twitter_accounts = [
        'ChartingProdigy' 
    ]
    
    tickers = [ticker.title for ticker in Tickers.objects.all()]
    tickerdict = scrape_twitter(twitter_accounts, tickers, .25)
    print(tickerdict)
    for key, value in tickerdict.items():
        print("aaaaaaaaa")
        ticker = Tickers.objects.get(title=key)
        Social_media_mentions.objects.create(ticker=ticker, mentions=value)
    print("cccccc")


    RedditAccounts =["r/wallstreetbets", "r/shortsqueeze"]
    print("now scraping reddit")
    reddit_ticker_dict = scrape_reddit(RedditAccounts, tickers, .25)

    for key, value in reddit_ticker_dict.items():
        instance = Social_media_mentions.objects.get(ticker=key)
        instance.mentions  += value
        instance.save()
    
@shared_task
def Working():
    user_email = UserEmail.objects.get(id=1)
    user_email.result += 1
    user_email.save()
    print("Current Work")

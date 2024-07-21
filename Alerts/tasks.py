from Alerts.models import Alerts_Details ,Ticker , Alert , Earning_Alert , Alert_13F
import requests
from datetime import date , timedelta
from QuizApp.models import UserEmail
from celery import shared_task
from .TwitterScraper import main as scrape_twitter
from .RedditScraper import main as scrape_reddit
from Alerts.OptionsScraper import main

def getIndicator(ticker , timespan , type):
    print("abvsd")
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type={type}&period=14&apikey={api_key}')
    # print(data.json())
    return data.json()

## rsi function ##
def rsi(timespan):
    # strategy_time = timespan
    tickers = Ticker.objects.all()
    # data = []
    for ticker in tickers:
        risk_level = None
        result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='rsi')
        if result != []:
            rsi_value = result[0]['rsi']
            # date = result[0]['date']
            # status = None
            if rsi_value > 70:
                status = 'Overbought'
                risk_level = 'Bearish'
            if rsi_value < 30:
                status = 'Underbought'
                risk_level = 'Bullish'
            message = f"Using rsi Strategy, The Ticker {ticker} , this Stock is {status} and its risk_level {risk_level}, with rsi value = {rsi_value} in date {date} "
            if risk_level != None:
                Alert.objects.create(ticker=ticker , strategy= 'RSI' ,strategy_time=timespan ,risk_level=risk_level , strategy_value = rsi_value )
                Alerts_Details.objects.create(ticker=ticker.symbol , strategy=f'RSI per {timespan}' , value=rsi_value , risk_level = risk_level,message=message)
            # return data

## ema function ##
def ema(timespan):
    strategy = f'EMA strategy per {timespan}'
    tickers = Ticker.objects.all()
    # data = []
    for ticker in tickers:
        result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='ema')
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
                Alert.objects.create(ticker=ticker , strategy= 'EMA' ,strategy_time=timespan ,risk_level=risk_level , strategy_value = ema_value )
                Alerts_Details.objects.create(ticker=ticker.symbol , strategy=f'{strategy} per {timespan}' , value=ema_value , risk_level = risk_level,message=message)
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
    ema(timespan='4hour')

## view for EMA  1hour ##
@shared_task
def EMA_1HOUR():
    ema(timespan='1hour')

@shared_task
def web_scraping_alerts():
    twitter_accounts = [
     "TriggerTrades", 'RoyLMattox', 'Mr_Derivatives', 'warrior_0719', 'ChartingProdigy', 
     'allstarcharts', 'yuriymatso', 'AdamMancini4', 'CordovaTrades','Barchart',
    ]
    
    tickers = [ticker.title for ticker in Ticker.objects.all()]
    tickerdict = scrape_twitter(twitter_accounts, tickers, .25)
    # print(tickerdict)
    for key, value in tickerdict.items():
        # print("aaaaaaaaa")
        message = f"people on social media are talking about {key}, you should check it out"
        Alert.objects.create(ticker=key, value=value, strategy="social_media_mentions", message=message)
    # print("cccccc")


    RedditAccounts =["r/wallstreetbets", "r/shortsqueeze"]
    # print("now scraping reddit")
    reddit_ticker_dict = scrape_reddit(RedditAccounts, tickers, .25)

    for key, value in reddit_ticker_dict.items():
        instance = Alerts_Details.objects.get(ticker=key)
        instance.mentions  += value
        instance.save()
    
@shared_task
def Working():
    user_email = UserEmail.objects.get(id=1)
    user_email.result += 1
    user_email.save()
    # print("Current Work")

@shared_task
def common_alert():
    today = date.today()
    alerts = Alert.objects.filter(date= today)
    Bearish_alerts = alerts.filter(risk_level='Bearish')
    Bullish_alerts = alerts.filter(risk_level='Bullish')
    mylists = [Bearish_alerts , Bullish_alerts]
    message = None
    for mylist in mylists:
        rsi_alerts = mylist.filter(strategy__startswith='RSI')
        ema_alerts = mylist.filter(strategy__startswith='EMA')
        new_list = []
        for rsi in rsi_alerts:
            for ema in ema_alerts:
                if rsi.ticker.symbol == ema.ticker.symbol:
                    if not ema.strategy.endswith('1hour'):
                        if rsi.ticker.symbol not in new_list:
                            new_list.append(rsi.ticker)
                            # message = f'{rsi.ticker} is common between rsi and ema and is {rsi.risk_level}!'
                            Alert.objects.create(ticker=rsi.ticker.symbol , strategy= 'EMA & RSI' ,risk_level=rsi.risk_level )

### task for 13F ###
list_of_CIK = ['0001067983']
@shared_task
def get_13f():
    api_key_fmd = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    day = date.today()
    strategy = '13F strategy'
    for cik in list_of_CIK:
        # response = requests.get(f'https://financialmodelingprep.com/api/v4/institutional-ownership/portfolio-holdings?date={day}&cik={cik}&page=0&apikey={api_key_fmd}')
        response = [
    {
        "date": "2021-09-30",
        "cik": "0001067983",
        "filingDate": "2021-11-15",
        "investorName": "BERKSHIRE HATHAWAY INC",
        "symbol": "AAPL",
        "securityName": "APPLE INC",
        "typeOfSecurity": "COM",
        "securityCusip": "037833100",
        "sharesType": "SH",
        "putCallShare": "Share",
        "investmentDiscretion": "DFND",
        "industryTitle": "ELECTRONIC COMPUTERS",
        "weight": 42.7776,
        "lastWeight": 41.465,
        "changeInWeight": 1.3126,
        "changeInWeightPercentage": 3.1656,
        "marketValue": 125529681000,
        "lastMarketValue": 121502087000,
        "changeInMarketValue": 4027594000,
        "changeInMarketValuePercentage": 3.3148,
        "sharesNumber": 887135554,
        "lastSharesNumber": 887135554,
        "changeInSharesNumber": 10000000,
        "changeInSharesNumberPercentage": 0,
        "quarterEndPrice": 141.2945214521,
        "avgPricePaid": 136.5555426888,
        "isNew": 'false',
        "isSoldOut": 'false',
        "ownership": 5.3118,
        "lastOwnership": 5.3348,
        "changeInOwnership": -0.023,
        "changeInOwnershipPercentage": -0.4305,
        "holdingPeriod": 23,
        "firstAdded": "2016-03-31",
        "performance": 4204116550.5744,
        "performancePercentage": 3.4704,
        "lastPerformance": 13281918464.8517,
        "changeInPerformance": -9077801914.2773,
        "isCountedForPerformance": 'true'
    },
    {
        "date": "2021-09-30",
        "cik": "0001067983",
        "filingDate": "2021-11-15",
        "investorName": "BERKSHIRE HATHAWAY INC",
        "symbol": "AAPL",
        "securityName": "APPLE INC",
        "typeOfSecurity": "COM",
        "securityCusip": "037833100",
        "sharesType": "SH",
        "putCallShare": "Share",
        "investmentDiscretion": "DFND",
        "industryTitle": "ELECTRONIC COMPUTERS",
        "weight": 42.7776,
        "lastWeight": 41.465,
        "changeInWeight": 1.3126,
        "changeInWeightPercentage": 3.1656,
        "marketValue": 125529681000,
        "lastMarketValue": 121502087000,
        "changeInMarketValue": 4027594000,
        "changeInMarketValuePercentage": 3.3148,
        "sharesNumber": 887135554,
        "lastSharesNumber": 887135554,
        "changeInSharesNumber": -523564,
        "changeInSharesNumberPercentage": 0,
        "quarterEndPrice": 141.2945214521,
        "avgPricePaid": 136.5555426888,
        "isNew": 'false',
        "isSoldOut": 'false',
        "ownership": 5.3118,
        "lastOwnership": 5.3348,
        "changeInOwnership": -0.023,
        "changeInOwnershipPercentage": -0.4305,
        "holdingPeriod": 23,
        "firstAdded": "2016-03-31",
        "performance": 4204116550.5744,
        "performancePercentage": 3.4704,
        "lastPerformance": 13281918464.8517,
        "changeInPerformance": -9077801914.2773,
        "isCountedForPerformance": 'true'
    },
]
        if response != []:
            for slice in response:
                changeInSharesNumber = slice['changeInSharesNumber']
                name = slice['investorName']
                symbol = slice['symbol']
                ticker = Ticker.objects.get(symbol=symbol)
                price = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={api_key_fmd}').json()
                price = price[0]['price']
                print(changeInSharesNumber)
                print(type(changeInSharesNumber))
                print(symbol)
                print(price)
                print(type(price))
                amount_of_investment = float(price) * abs(changeInSharesNumber)
                print(amount_of_investment)
                print(type(amount_of_investment))
                if amount_of_investment >= 1000000:
                    if changeInSharesNumber > 0 :
                        transaction = 'bought'
                    else:
                        transaction = 'sold'
                    message = f'investor ({name}) {transaction} the amount of shares of {symbol}({price}$) = {changeInSharesNumber} and the total price of it is {amount_of_investment}'
                    Alerts_Details.objects.create(ticker='Look out' , strategy=strategy , value=amount_of_investment , risk_level = 'big investment',message=message)
                    Alert_13F.objects.create(investor_name = name , transaction_tybe = transaction , num_shares = changeInSharesNumber , ticker=ticker ,ticker_price=price , amount_of_investment=amount_of_investment)


### function for Earning strategy ###
def Earnings(duration):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    ## today date ##
    today = date.today()
    thatday = today + timedelta(days=duration) ## date after period time ##
    ## response of the api ##
    response = requests.get(f'https://financialmodelingprep.com/api/v3/earning_calendar?from={thatday}&to={thatday}&apikey={api_key}')
    # print(response.json())
    if response.json() != []:
        list_ticker= []
        data= []
        for slice in response.json():
            Estimated_EPS = slice['epsEstimated']
            testy = '.' in slice['symbol']
            if not testy:
                if Estimated_EPS != None :
                    ticker = slice['symbol']
                    ticker2 = Ticker.objects.get(symbol=ticker)
                    time = slice['time']
                    Estimated_Revenue = slice['revenueEstimated']
                    list_ticker.append(ticker)
                    data.append({'ticker':ticker , 'strategy':'Earnings' ,'message':f'{ticker} after {duration} days its , Estimated Revenue={Estimated_Revenue}, time={time} , '})
                    # Alert.objects.create(ticker=ticker2 , strategy= 'Earning' ,strategy_time= duration ,risk_level=risk_level , strategy_value = rsi_value )

    ## get all Expected Moves by Scraping ##
    result = main(list_ticker)
    for x in result.items():
        for y in data:
            if x[0] == y['ticker']:
                y['Expected_Moves'] = x[1]
                Expected_Moves = x[1]
                y['message'] += f'Expected Moves={x[1]}'
                Alerts_Details.objects.create(ticker=ticker , strategy='Earning' , message=y['message'])
                Earning_Alert.objects.create(ticker=ticker2 ,strategy= 'Earning', strategy_time = duration , Estimated_Revenue = Estimated_Revenue, Estimated_EPS = Estimated_EPS , Expected_Moves=Expected_Moves , earning_time=time)

## Earning strategy in 15 days ##
@shared_task
def earning15():
    Earnings(15)

## Earning strategy in 30 days ##
@shared_task
def earning30():
    Earnings(30)
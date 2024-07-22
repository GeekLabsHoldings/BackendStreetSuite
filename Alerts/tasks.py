from Alerts.models import Alerts_Details ,Ticker , Rsi_Alert,EMA_Alert , Earning_Alert , Alert_13F , Alert , Result , Industry
import requests
from datetime import  timedelta , datetime
from datetime import date as dt
from QuizApp.models import UserEmail
from celery import shared_task
from .TwitterScraper import main as scrape_twitter
from .RedditScraper import main as scrape_reddit
from Alerts.OptionsScraper import main
import logging

logger = logging.getLogger('celery') 

## task for Earning strategy ##
@shared_task
def Earnings(duration):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    ## today date ##
    today = dt.today()
    thatday = today + timedelta(days=duration) ## date after period time ##
    all_symbols = Ticker.objects.all()
    symbol_list = []
    for symbol in all_symbols:
        symbol_list.append(symbol.symbol)
    ## response of the api ##
    response = requests.get(f'https://financialmodelingprep.com/api/v3/earning_calendar?from={thatday}&to={thatday}&apikey={api_key}')
    # print(response.json())
    if response.json() != []:
        list_ticker= []
        data= []
        for slice in response.json()[:100]:
            Estimated_EPS = slice['epsEstimated']
            testy = '.' in slice['symbol']
            if not testy:
                if Estimated_EPS != None :
                    ticker = slice['symbol']
                    ticker_data = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={api_key}').json()
                    industry_name = ticker_data[0]['industry']
                    name = ticker_data[0]['companyName']
                    market_cap = ticker_data[0]['mktCap']
                    try:
                        ticker2 = Ticker.objects.get(symbol=ticker)
                    except :
                        industry , created = Industry.objects.get_or_create(type=industry_name)
                        ticker2 = Ticker.objects.create(symbol=ticker , name=name ,market_cap=market_cap , industry=industry)
                    finally:
                        time = slice['time']
                        Estimated_Revenue = slice['revenueEstimated']
                        list_ticker.append(ticker)
                        data.append({'ticker':ticker , 'strategy':'Earnings' ,'Estimated_Revenue':Estimated_Revenue, 'time':time , 'Estimated_EPS':Estimated_EPS ,})
                        # Alert.objects.create(ticker=ticker2 , strategy= 'Earning' ,strategy_time= duration ,risk_level=risk_level , strategy_value = rsi_value )

    ## get all Expected Moves by Scraping ##
    result = main(list_ticker)
    for x in result.items():
        for y in data:
            if x[0] == y['ticker']:
                y['Expected_Moves'] = x[1]
                Expected_Moves = x[1]
                # y['message'] += f'Expected Moves={x[1]}'
                ticker2 = y['ticker']
                ticker = Ticker.objects.get(symbol=ticker2)
                Estimated_Revenue = y['Estimated_Revenue']
                Estimated_EPS = y['Estimated_EPS']
                time = y['time']
                # Alerts_Details.objects.create(ticker=ticker , strategy='Earning' , message=y['message'])
                Earning_Alert.objects.create(ticker=ticker ,strategy= 'Earning', strategy_time = duration , Estimated_Revenue = Estimated_Revenue, Estimated_EPS = Estimated_EPS , Expected_Moves=Expected_Moves , earning_time=time)

### method to get the result of strategy ###
def get_result(ticker , strategy , time_frame , value ):
    logger.info("geting result")
    # day_time = datetime.now()
    day = dt.today()
    print(ticker.symbol)
    print(strategy)
    print("ll")
    try:
        if time_frame == '1day':
            days = 1
            date = day - timedelta(days=days)
            print("kk")
            ticker_data = Alert.objects.filter(ticker=ticker , strategy=strategy , strategy_time=time_frame)
            
            print(ticker_data.json())
        else:
            print('oo')
            ticker_data = Alert.objects.filter(ticker=ticker, strategy=strategy, strategy_time=time_frame).latest('id')
            print(ticker_data.ticker.symbol)
        ## get the risk level and value of previuos ticker results ##
        print("salama")
        ticker_risk_level = ticker_data.risk_level
        ticker_value = ticker_data.strategy_value
        ###
        # strategyy = strategy[:2]
        # time_framy = strategy[-4:].strip()
        ###
        print(ticker_value)
        print(ticker_risk_level)
        print(time_frame)
        result = Result.objects.filter(strategy=strategy ,time_frame=time_frame).latest('id')
        print(result.strategy ,result.time_frame )
        if ticker_risk_level == 'Bearish':
            if ticker_value > value :
                result.success += 1
                result.save()
                print("success +=1")
        if ticker_risk_level == 'Bullish':
            if ticker_value < value :
                result.success += 1
                result.total += 1
                result.save()
                print("success +=1")
            else:
                print("not bigger")
        print("total +=1")
    except:
        print('alert not exists')
    finally:
        print("finaly")
## method to get data of ticker by api ##
def getIndicator(ticker , timespan , type):
    print("abvsd")
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type={type}&period=14&apikey={api_key}')
    # print(data.json())
    return data.json()

## rsi function ##
def rsi(timespan):
    logger.info("geting rsi")
    # strategy_time = timespan
    tickers = Ticker.objects.all()
    # data = []
    for ticker in tickers:
        risk_level = None
        result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='rsi')
        status = None
        if result != []:
            rsi_value = result[0]['rsi']
            date = result[0]['date']
            # status = None
            if rsi_value > 70:
                status = 'Overbought'
                risk_level = 'Bearish'
            if rsi_value < 30:
                status = 'Underbought'
                risk_level = 'Bullish'
            # message = f"Using rsi Strategy, The Ticker {ticker} , this Stock is {status} and its risk_level {risk_level}, with rsi value = {rsi_value} in date {date} "
            if risk_level != None:
                # get_result(ticker=ticker,strategy='RSI',time_frame=timespan,value=rsi_value ,model=Rsi_Alert)
                Rsi_Alert.objects.create(ticker=ticker , strategy= 'RSI' ,strategy_time=timespan ,risk_level=risk_level , rsi_value = rsi_value )
                # Alert.objects.create(ticker=ticker , strategy= 'RSI' ,strategy_time=timespan ,risk_level=risk_level , strategy_value = rsi_value )
                # Alerts_Details.objects.create(ticker=ticker.symbol , strategy=f'RSI per {timespan}' , value=rsi_value , risk_level = risk_level,message=message)
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
                # get_result(ticker=ticker,strategy='EMA',time_frame=timespan,value=ema_value )   
                EMA_Alert.objects.create(ticker=ticker , strategy= 'EMA' ,strategy_time=timespan ,risk_level=risk_level , ema_value = ema_value )
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
    
    tickers = [ticker.symbol for ticker in Ticker.objects.all()]
    tickerdict = scrape_twitter(twitter_accounts, tickers, .25)
    
    for key, value in tickerdict.items():
        ticker = Ticker.objects.get(symbol=key)
        Alert.objects.create(ticker=ticker, strategy_value=value, strategy="social_media_mentions")
   


    RedditAccounts =["r/wallstreetbets", "r/shortsqueeze"]
    # print("now scraping reddit")
    reddit_ticker_dict = scrape_reddit(RedditAccounts, tickers, .25)

    for key, value in reddit_ticker_dict.items():
        ticker = Ticker.objects.get(symbol=key)
        instance = Alert.objects.get(ticker=ticker)
        instance.strategy_value  += value
        instance.save()
    
@shared_task
def Working():
    user_email = UserEmail.objects.get(id=1)
    user_email.result += 1
    user_email.save()
    # print("Current Work")

@shared_task
def common_alert():
    day = dt.today()
    ## get rsi and ema alerts ##
    rsi_bearish = Rsi_Alert.objects.filter(risk_level='Bearish' , date=day)
    rsi_bullish = Rsi_Alert.objects.filter(risk_level='Bullish' , date=day)
    ema_bearish = EMA_Alert.objects.filter(risk_level='Bearish' , date=day)
    ema_bullish = EMA_Alert.objects.filter(risk_level='Bullish' , date=day)
    data = []
    for alertx in rsi_bearish:
        for alerty in ema_bearish:
            if alertx.ticker == alerty.ticker:
                if alertx.ticker.symbol not in data:
                    data.append(alertx.ticker.symbol)
                    Rsi_Alert.objects.create(ticker=alertx.ticker , strategy= 'RSI & EMA', risk_level='Bearish')
    data = []
    for alertx in rsi_bullish:
        for alerty in ema_bullish:
            if alertx.ticker == alerty.ticker:
                if alertx.ticker.symbol not in data:
                    data.append(alertx.ticker.symbol)
                    Rsi_Alert.objects.create(ticker=alertx.ticker , strategy= 'RSI & EMA', risk_level='Bullish')


## task for Relative Volume strategy ##
@shared_task
def volume():
    tickers = Ticker.objects.all()
    for ticker in tickers:
        response = requests.get(f'https://financialmodelingprep.com/api/v3/quote/{ticker.symbol}?apikey=juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2').json()
        volume = response[0]['volume']
        avgVolume = response[0]['avgVolume']
        if volume > avgVolume:
            value2 = int(volume) -int(avgVolume)
            value = (int(value2)/int(avgVolume)) * 100
            Alert.objects.create(ticker=ticker ,strategy='Relative Volume' ,strategy_value=value ,risk_level= 'overbought avarege')


### task for 13F ###
list_of_CIK = ['0001067983']
@shared_task
def get_13f():
    api_key_fmd = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    day = dt.today()
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
# def Earnings(duration):
#     api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
#     ## today date ##
#     today = dt.today()
#     thatday = today + timedelta(days=duration) ## date after period time ##
#     ## response of the api ##
#     response = requests.get(f'https://financialmodelingprep.com/api/v3/earning_calendar?from={thatday}&to={thatday}&apikey={api_key}')
#     # print(response.json())
#     if response.json() != []:
#         list_ticker= []
#         data= []
#         for slice in response.json():
#             Estimated_EPS = slice['epsEstimated']
#             testy = '.' in slice['symbol']
#             if not testy:
#                 if Estimated_EPS != None :
#                     ticker = slice['symbol']
#                     ticker2 = Ticker.objects.get(symbol=ticker)
#                     time = slice['time']
#                     Estimated_Revenue = slice['revenueEstimated']
#                     list_ticker.append(ticker)
#                     data.append({'ticker':ticker , 'strategy':'Earnings' ,'message':f'{ticker} after {duration} days its , Estimated Revenue={Estimated_Revenue}, time={time} , '})
                    # Alert.objects.create(ticker=ticker2 , strategy= 'Earning' ,strategy_time= duration ,risk_level=risk_level , strategy_value = rsi_value )

    ## get all Expected Moves by Scraping ##
    result = main(list_ticker)
    for x in result.items():
        for y in data:
            if x[0] == y['ticker']:
                y['Expected_Moves'] = x[1]
                Expected_Moves = x[1]
                y['message'] += f'Expected Moves={x[1]}'
                # Alerts_Details.objects.create(ticker=ticker , strategy='Earning' , message=y['message'])
                Earning_Alert.objects.create(ticker=ticker2 ,strategy= 'Earning', strategy_time = duration , Estimated_Revenue = Estimated_Revenue, Estimated_EPS = Estimated_EPS , Expected_Moves=Expected_Moves , earning_time=time)

## Earning strategy in 15 days ##
@shared_task
def earning15():
    Earnings(15)

## Earning strategy in 30 days ##
@shared_task
def earning30():
    Earnings(30)
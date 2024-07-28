from Alerts.models import Ticker , Rsi_Alert,EMA_Alert , Earning_Alert , Alert_13F  , Result , Industry, Alert_InsiderBuyer , Alert
import requests
from datetime import  timedelta
from datetime import date as dt , datetime
from celery import shared_task
from .TwitterScraper import main as scrape_web
from .ShortIntrestScraper  import main as scrape_short_intrest
from Alerts.OptionsScraper import main as earning_scraper
from celery.exceptions import SoftTimeLimitExceeded
from django.db.models import Q
import redis
from django.core.cache import cache

# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
# def get_tickers():
#     redis_client.set("tickers")

def get_cached_queryset():
    queryset = cache.get("tickerlist")
    if not queryset:
        print("gotttt")
        queryset = Ticker.objects.all()
        cache.set("tickerlist", queryset, timeout=86400)
    return queryset

## task for Earning strategy ##
def Earnings(duration):
    # value = redis_client.get('tickers')
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    ## today date ##
    today = dt.today()
    thatday = today + timedelta(days=duration) ## date after period time ##
    ## response of the api ##
    response = requests.get(f'https://financialmodelingprep.com/api/v3/earning_calendar?from={thatday}&to={thatday}&apikey={api_key}')
    if response.json() != []:
        list_ticker= []
        data= []
        for slice in response.json():
            Estimated_EPS = slice['epsEstimated']
            dotted_ticker = '.' in slice['symbol']
            if not dotted_ticker:
                if Estimated_EPS != None :
                    ticker = slice['symbol']
                    ticker_data = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={api_key}').json()
                    if ticker_data != []:
                        industry_name = ticker_data[0]['industry']
                        company_name = ticker_data[0]['companyName']
                        market_cap = ticker_data[0]['mktCap']
                        try:
                            ticker2 = Ticker.objects.get(symbol=ticker)
                        except :
                            industry , created = Industry.objects.get_or_create(type=industry_name)
                            ticker2 = Ticker.objects.create(symbol=ticker , name=company_name ,market_cap=market_cap , industry=industry)
                        finally:
                            time = slice['time']
                            Estimated_Revenue = slice['revenueEstimated']
                            list_ticker.append(ticker)
                            data.append({'ticker':ticker , 'strategy':'Earnings' ,'Estimated_Revenue':Estimated_Revenue, 'time':time , 'Estimated_EPS':Estimated_EPS ,})

    ## get all Expected Moves by Scraping ##
    result = earning_scraper(list_ticker)
    for x in result.items():
        for y in data:
            if x[0] == y['ticker']:
                Expected_Moves = x[1]
                ticker2 = y['ticker']
                ticker = Ticker.objects.get(symbol=ticker2)
                Estimated_Revenue = y['Estimated_Revenue']
                Estimated_EPS = y['Estimated_EPS']
                time = y['time']
                Alert.objects.create(ticker=ticker ,strategy= 'Earning', 
                                     time_frame = str(duration) , Estimated_Revenue = Estimated_Revenue, 
                                     Estimated_EPS = Estimated_EPS , Expected_Moves=Expected_Moves , earning_time=time)
### method to get the result of strategy ###
def get_result(ticker , strategy , time_frame  ):
    # day_time = datetime.now()
    day = dt.today()
    print(ticker.symbol)
    print(strategy)
    print("ll")
    try:
        if time_frame == '1day':
            date_day = day - timedelta(days=1)
            print("kk")
            ticker_data = EMA_Alert.objects.get(ticker=ticker , strategy_time=time_frame , date=date_day)
            print('1day')
            print(ticker_data.strategy)
        else:
            print('oo')
            ticker_data = EMA_Alert.objects.filter(ticker=ticker,strategy_time=time_frame).latest('id')
            print(ticker_data.ticker.symbol)
        ## get the risk level and value of previuos ticker results ##
        print("salama")
        ticker_risk_level = ticker_data.risk_level
        print(ticker_risk_level)
        ticker_value = ticker_data.strategy_value
        ###
        # strategyy = strategy[:2]
        # time_framy = strategy[-4:].strip()
        ###
        print(ticker_value)
        print(time_frame)
        result = Result.objects.get(strategy=strategy ,time_frame=time_frame)
        print(result.strategy ,result.time_frame )
        if ticker_risk_level == 'Bearish':
            if ticker_value > ticker_value :
                result.success += 1
                result.save()
                print("success +=1")
            else:
                result.total += 1
                result.save()
                print("not giger")
        elif ticker_risk_level == 'Bullish':
            if ticker_value > ticker_value :
                result.success += 1
                result.total += 1
                result.save()
                print("success +=1")
            else:
                result.total += 1
                result.save()
                print("not smaller")
        print("total +=1")
    except:
        print('alert not exists')
    finally:
        print("finaly")

## method to get data of ticker by api ##
def getIndicator(ticker , timespan , type):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type={type}&period=14&apikey={api_key}')
    return data.json()

## rsi function ##
def rsi(timespan):
    print("getting RSI")
    tickers = get_cached_queryset()

    for ticker in tickers:
        
        risk_level = None
        result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='rsi')
        if result != []:
            # print(result)
            try:
                rsi_value = result[0]['rsi']
            except BaseException:
                continue
            if rsi_value > 70:
                risk_level = 'Bearish'
            if rsi_value < 30:
                risk_level = 'Bullish'
            if risk_level != None:
                
                alert = Alert.objects.create(ticker=ticker , strategy= 'RSI' ,time_frame=timespan ,risk_level=risk_level , result_value = rsi_value )
                return alert

## ema function ##
def ema(timespan):
    print("getting EMA")
    tickers = get_cached_queryset()
    for ticker in tickers:
        result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='ema')
        if result != []:
            risk_level = None
            ema_value = result[0]['ema']
            current_price = result[0]['close']
            old_price = result[1]['close']
            if ema_value < current_price and ema_value > old_price:
                risk_level = 'Bullish'
            if ema_value > current_price and ema_value < old_price:
                risk_level = 'Bearish'
            if risk_level != None:   
                Alert.objects.create(ticker=ticker , strategy= 'EMA' ,time_frame=timespan ,risk_level=risk_level , result_value = ema_value )

## endpint for RSI 4 hours ##
@shared_task
def RSI_4hour():
    current_alert = rsi(timespan='4hour')
    alert = cache.get("RSI 4hour")
    if not alert:
        cache.set("RSI 4hour", current_alert, timeout=86400)
        print("first result cache")
    if (alert.risk_level == 'Bearish' and current_alert.result_value < 70) or (alert.risk_level == 'Bullish' and current_alert.result_value > 30):
        cache.set("RSI 4hour", alert, timeout=86400)
        print("cahed after finishing the first result")
        result = Result.objects.get(strategy='RSI',time_frame='4hour')
        result.success += 1
        result.total += 1
        result.save()
    else:
        cache.set("RSI 4hour", alert, timeout=86400)
        print("cahed after finishing the first result")
        result = Result.objects.get(strategy='RSI',time_frame='4hour')
        result.total += 1
        result.save()
    
## endpint for RSI 1day ##
@shared_task
def RSI_1day():
    current_alert = rsi(timespan='1day')
    alert = cache.get("RSI 1day")
    if not alert:
        cache.set("RSI 1day", current_alert, timeout=86400)
    if (alert.risk_level == 'Bearish' and current_alert.result_value < 70) or (alert.risk_level == 'Bullish' and current_alert.result_value > 30):
        cache.set("RSI 1day", alert, timeout=86400)
        result = Result.objects.get(strategy='RSI',time_frame='1day')
        result.success += 1
        result.total += 1
        result.save()
    else:
        cache.set("RSI 1day", alert, timeout=86400)
        result = Result.objects.get(strategy='RSI',time_frame='1day')
        result.total += 1
        result.save()

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


@shared_task(time_limit=420, soft_time_limit=420)
def web_scraping_alerts():
    try:
        twitter_accounts = [
        "TriggerTrades", 'RoyLMattox', 'Mr_Derivatives', 'warrior_0719', 'ChartingProdigy', 
        'allstarcharts', 'yuriymatso', 'AdamMancini4', 'CordovaTrades','Barchart',
        ]
        RedditAccounts =["r/wallstreetbets", "r/shortsqueeze"]

        # tickers = [ticker.symbol for ticker in Ticker.objects.all()]
        tickers = get_cached_queryset()
        tickerlist = []
        for ticker in tickers:
            tickerlist.append(ticker.symbol)

        tickerdict = scrape_web(twitter_accounts, tickers, .25, RedditAccounts)
        if tickerdict == None:
            print("could not scrape")
            return 1
        for key, value in tickerdict.items():
            for ticker in tickers:
                if ticker.symbol == key:
                    Alert.objects.create(ticker=ticker, result_value=value, strategy="People's Opinion")
            
    except SoftTimeLimitExceeded:
        print("scraping time limit exceeded")

# @shared_task
# def common_alert():
#     day = dt.today()
#     ## get rsi and ema alerts ##
#     rsi_bearish = Rsi_Alert.objects.filter(risk_level='Bearish' , date=day)
#     rsi_bullish = Rsi_Alert.objects.filter(risk_level='Bullish' , date=day)
#     ema_bearish = EMA_Alert.objects.filter(risk_level='Bearish' , date=day)
#     ema_bullish = EMA_Alert.objects.filter(risk_level='Bullish' , date=day)
#     data = []
#     for alertx in rsi_bearish:
#         for alerty in ema_bearish:
#             if alertx.ticker == alerty.ticker:
#                 if alertx.ticker.symbol not in data:
#                     data.append(alertx.ticker.symbol)
#                     Rsi_Alert.objects.create(ticker=alertx.ticker , strategy= 'RSI & EMA', risk_level='Bearish')
#     data = []
#     for alertx in rsi_bullish:
#         for alerty in ema_bullish:
#             if alertx.ticker == alerty.ticker:
                # if alertx.ticker.symbol not in data:
                    # data.append(alertx.ticker.symbol)
                    # Rsi_Alert.objects.create(ticker=alertx.ticker , strategy= 'RSI & EMA', risk_level='Bullish')
# @shared_task
# def common_alert():
#     day = dt.today()
#     ## get rsi and ema alerts ##
#     alerts = Alert.objects.filter(
#         Q(strategy='RSI', date=day) | Q(strategy='EMA', date=day)
#         )
#     ## looping in alerts ##
#     data = []
#     for alert in alerts:
#         for ema_alert in ema_alerts:
#             if rsi_alert.risk_level == ema_alert.risk_level and rsi_alert.ticker == ema_alert.ticker:
#                 if rsi_alert.ticker.symbol not in data:
#                     data.append(rsi_alert.ticker.symbol)
#                     Alert.objects.create(ticker=rsi_alert.ticker , strategy= 'RSI & EMA', risk_level=rsi_alert.risk_level)

## task for Relative Volume strategy ##
@shared_task
def volume():
    tickers = get_cached_queryset()
    for ticker in tickers:
        response = requests.get(f'https://financialmodelingprep.com/api/v3/quote/{ticker.symbol}?apikey=juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2').json()
        if response != []:
            volume = response[0]['volume']
            avgVolume = response[0]['avgVolume']
            if volume > avgVolume:
                value2 = int(volume) -int(avgVolume)
                value = (int(value2)/int(avgVolume)) * 100
                Alert.objects.create(ticker=ticker ,strategy='Relative Volume' ,result_value=value ,risk_level= 'overbought avarege')


### task for 13F ###
list_of_CIK = ['0001067983']
@shared_task
def get_13f():
    print("getting 13F")
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
                ticker_data = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={api_key_fmd}').json()
                price = ticker_data[0]['price']
                amount_of_investment = float(price) * abs(changeInSharesNumber)
                if amount_of_investment >= 1000000:
                    if changeInSharesNumber > 0 :
                        transaction = 'bought'
                    else:
                        transaction = 'sold'
                        Alert.objects.create(investor_name = name , transaction_tybe = transaction , 
                                             shares_quantity = changeInSharesNumber , ticker= ticker ,
                                             ticker_price=price , amount_of_investment=amount_of_investment)


## Earning strategy in 15 days ##
@shared_task
def earning15():
    Earnings(15)

## Earning strategy in 30 days ##
@shared_task
def earning30():
    Earnings(30)

@shared_task
def Insider_Buyer():
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    tickers = get_cached_queryset()
    now = datetime.now()    
    for ticker in tickers:
        response = requests.get(f'https://financialmodelingprep.com/api/v4/insider-trading?symbol={ticker.symbol}&page=0&apikey={api_key}')
        if response != []:
            filing_date_str = response[0]['filingDate']
            filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d %H:%M:%S")
            if now.date() == filing_date.date() and now.hour == filing_date.hour: 
                Alert.objects.create(ticker=ticker, strategy='Insider Buyer', ticker_price=response[0]['price'],
                            transaction_date=response[0]['transactionDate'], investor_name=response[0]['reportingName'],
                            job_title=response[0]["typeOfOwner"], shares_quantity=response[0]["securitiesTransacted"],
                              transaction_type=response[0]["transactionType"], filling_date=str(filing_date_str))



## task for Unusual Option Buys strategy ##
@shared_task
def unusual_avg():
    tickers = get_cached_queryset()
    token = 'a4c1971d-fbd2-417e-a62d-9b990309a3ce'  
    ## for Authentication on request ##
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'  # Optional, depending on the API requirements
    }
    ## looping on tickers ##
    for ticker in tickers:
        response = requests.get(
            f'https://api.unusualwhales.com/api/stock/{ticker.symbol}/options-volume',
            headers=headers
        ).json()
        
        try:
            ## to get avg of call transaction ##
            avg_30_day_call_volume = response['data'][0]['avg_30_day_call_volume']
            ## average number of put transaction ##
            avg_30_day_put_volume = response['data'][0]['avg_30_day_put_volume']
            ### get all cntracts for each ticker ###
            contract_options = requests.get(f'https://api.unusualwhales.com/api/stock/{ticker.symbol}/option-contracts',headers=headers).json()['data']
            try:
                ## looping on each contract ##
                for contract in contract_options:
                    volume = contract['volume']
                    contract_id = contract['option_symbol']
                    if contract_id[-9] == 'C':
                        if float(volume) > float(avg_30_day_call_volume):
                            Alert.objects.create(ticker=ticker 
                                ,strategy='Unusual Option Buys' ,time_frame='1day' ,result_value=volume, 
                                risk_level= 'Call' ,investor_name=contract_id , amount_of_investment= avg_30_day_call_volume)
                    else:
                        if float(volume) > float(avg_30_day_put_volume):
                            Alert.objects.create(ticker=ticker 
                                ,strategy='Unusual Option Buys' ,time_frame='1day' ,result_value=volume, 
                                risk_level= 'Put' ,investor_name=contract_id , amount_of_investment= avg_30_day_put_volume)
                            # data.append(f'There is unusaual activity in the option contract {contract_id} C 17/2, the average volume is {volume}, and the current volume is {avg_30_day_put_volume}, which is put.')
            except BaseException:
                continue
        except BaseException :
            continue


@shared_task
def short_interset():
    tickers = get_cached_queryset()
    data = []
    ## looping in tickers ##
    for ticker in tickers:
        data.append(ticker.symbol)
    ## get all short interest value ##
    short_interset_values = scrape_short_intrest(data)
    ## looping in results ##
    for key , value in short_interset_values.items():
        ticker = Ticker.objects.get(symbol=key)
        Alert.objects.create(ticker=ticker,strategy='Short Interest',result_value=value)




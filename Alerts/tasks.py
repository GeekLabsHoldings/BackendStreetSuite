from Alerts.models import Ticker , Result , Industry,  Alert
import requests
from datetime import  timedelta
from datetime import date as dt , datetime
from celery import shared_task
from .TwitterScraper import main as scrape_web
from .ShortIntrestScraper  import short_interest_scraper
from Alerts.OptionsScraper import earning_scraping
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
    print(thatday)
    ## response of the api ##
    response = requests.get(f'https://financialmodelingprep.com/api/v3/earning_calendar?from={thatday}&to={thatday}&apikey={api_key}')
    if response.json() != []:
        for slice in response.json():
            Estimated_EPS = slice['epsEstimated']
            dotted_ticker = '.' in slice['symbol']
            if not dotted_ticker:
                if Estimated_EPS != None :
                    ticker = slice['symbol']
                    print(ticker)
                    try:
                        ticker2 = Ticker.objects.get(symbol=ticker)
                        time = slice['time']
                        Estimated_Revenue = slice['revenueEstimated']
                        if Estimated_Revenue != None:
                            Expected_Moves = earning_scraping(ticker2.symbol) 
                            Alert.objects.create(ticker=ticker2 ,strategy= 'Earning', 
                                        time_frame = str(duration) , Estimated_Revenue = Estimated_Revenue, 
                                        Estimated_EPS = Estimated_EPS , Expected_Moves=Expected_Moves , earning_time=time)
                    except:
                        continue

## method to get data of ticker by api ##
def getIndicator(ticker , timespan , type):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type={type}&period=14&apikey={api_key}')
    return data.json()

## rsi function ##
def rsi(timespan):
    tickers = get_cached_queryset()
    is_cached = True
    previous_rsi_alerts = cache.get(f"RSI_{timespan}")
    if not previous_rsi_alerts:
        is_cached = False
    rsi_data = []
    for ticker in tickers:
        risk_level = None
        result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='rsi')
        if result != []:
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
                if is_cached:
                    for previous_alert in previous_rsi_alerts:
                        if previous_alert.ticker.symbol == alert.ticker.symbol:
                            if (
                                (previous_alert.risk_level == 'Bearish' and alert.result_value < 70) or 
                                (previous_alert.risk_level == 'Bullish' and alert.result_value > 30)
                            ):
                                result = Result.objects.get(strategy='RSI',time_frame=timespan)
                                result.success += 1
                                result.total += 1
                                result.result_value = (result.success / result.total)*100
                                result.save()
                            else:
                                result = Result.objects.get(strategy='RSI',time_frame=timespan)
                                result.total += 1
                                result.result_value = (result.success / result.total)*100
                                result.save()
                            previous_rsi_alerts.remove(previous_alert)
                            break    
                rsi_data.append(alert)
    if is_cached:
        cache.delete(f"RSI_{timespan}")
    cache.set(f"RSI_{timespan}", rsi_data, timeout=86400*2)

## ema function ##
def ema(timespan):
    print("getting EMA")
    tickers = get_cached_queryset()
    ema_data = []
    for ticker in tickers:
        try:
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
                    alert = Alert.objects.create(ticker=ticker , strategy= 'EMA' ,time_frame=timespan ,risk_level=risk_level , result_value = ema_value )
                    ema_data.append(alert)
        except:
            continue
    


## endpint for RSI 4 hours ##
@shared_task
def RSI_4hour():
    rsi(timespan='4hour')
    
## endpint for RSI 1day ##
@shared_task
def RSI_1day():
    current_rsi_alerts = rsi(timespan='1day')
    previous_rsi_alerts = cache.get("RSI_1day")
    if not previous_rsi_alerts:
        cache.set("RSI_1day", current_rsi_alerts, timeout=86400)
        previous_rsi_alerts = cache.get("RSI_1day")  
    for previous_alert in previous_rsi_alerts:
        for current_alert in current_rsi_alerts:
            if current_alert.ticker.symbol == previous_alert.ticker.symbol:
                if (
                    (previous_alert.risk_level == 'Bearish' and current_alert.result_value < 70) or 
                    (previous_alert.risk_level == 'Bullish' and current_alert.result_value > 30)
                ):                    
                    
                    result = Result.objects.get(strategy='RSI',time_frame='1day')
                    result.success += 1
                    result.total += 1
                    result.result_value = (result.success / result.total)*100
                    result.save()
                else:
                    result = Result.objects.get(strategy='RSI',time_frame='1day')
                    result.total += 1
                    result.result_value = (result.success / result.total)*100
                    result.save()
                break
    cache.delete('RSI_1day')
    cache.set('RSI_1day', current_rsi_alerts, timeout=86400)

## view for EMA  1day ##
@shared_task
def EMA_DAY():
    current_ema_alerts = ema(timespan='1day')
    previous_ema_alerts = cache.get("EMA_1day")
    if not previous_ema_alerts:
        cache.set("EMA_1day", current_ema_alerts, timeout=86400*2)
        previous_ema_alerts = cache.get("EMA_1day")  
    for previous_alert in previous_ema_alerts:
        for current_alert in current_ema_alerts:
            if current_alert.ticker.symbol == previous_alert.ticker.symbol:
                if (
                    (previous_alert.risk_level == 'Bearish' and current_alert.result_value < 70) or 
                    (previous_alert.risk_level == 'Bullish' and current_alert.result_value > 30)
                ):                    
                    
                    result = Result.objects.get(strategy='EMA',time_frame='1day')
                    result.success += 1
                    result.total += 1
                    result.result_value = (result.success / result.total)*100
                    result.save()
                else:
                    result = Result.objects.get(strategy='EMA',time_frame='1day')
                    result.total += 1
                    result.result_value = (result.success / result.total)*100
                    result.save()
                break
    cache.delete('EMA_1day')
    cache.set('EMA_1day', current_ema_alerts, timeout=86400)
## view for EMA  4hour  ##
@shared_task
def EMA_4HOUR():
    
    current_ema_alerts = ema(timespan='4hour')
    previous_ema_alerts = cache.get("EMA_4hour")
    if not previous_ema_alerts:
        cache.set("EMA_4hour", current_ema_alerts, timeout=86400)
        previous_ema_alerts = cache.get("EMA_4hour")  
    for previous_alert in previous_ema_alerts:
        for current_alert in current_ema_alerts:
            if current_alert.ticker.symbol == previous_alert.ticker.symbol:
                if (
                    (previous_alert.risk_level == 'Bearish' and current_alert.result_value < 70) or 
                    (previous_alert.risk_level == 'Bullish' and current_alert.result_value > 30)
                ):                    
                    
                    result = Result.objects.get(strategy='EMA',time_frame='4hour')
                    result.success += 1
                    result.total += 1
                    result.result_value = (result.success / result.total)*100
                    result.save()
                else:
                    result = Result.objects.get(strategy='EMA',time_frame='4hour')
                    result.total += 1
                    result.result_value = (result.success / result.total)*100
                    result.save()
                break
    cache.delete('EMA_4hour')
    cache.set('EMA_4hour', current_ema_alerts, timeout=86400)

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



## task for Relative Volume strategy ##
@shared_task
def volume():
    tickers = get_cached_queryset()
    for ticker in tickers:
        response = requests.get(f'https://financialmodelingprep.com/api/v3/quote/{ticker.symbol}?apikey=juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2').json()
        if response != []:
            volume = response[0]['volume']
            avgVolume = response[0]['avgVolume']
            if volume > avgVolume and avgVolume != 0:
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
        response = requests.get(f'https://financialmodelingprep.com/api/v4/insider-trading?symbol={ticker.symbol}&page=0&apikey={api_key}').json()
        if response != []:
            for i in range(len(response)):
                filing_date_str = response[i]['filingDate']
                filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d %H:%M:%S")
                if now.date() == filing_date.date() and now.hour == filing_date.hour: 
                    Alert.objects.create(ticker=ticker, strategy='Insider Buyer', ticker_price=response[i]['price'],
                                transaction_date=response[i]['transactionDate'], investor_name=response[i]['reportingName'],
                                job_title=response[i]["typeOfOwner"], shares_quantity=response[i]["securitiesTransacted"],
                                  transaction_type=response[i]["transactionType"], filling_date=str(filing_date_str))
                else:
                    break



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
    ## looping in tickers ##
    for ticker in tickers:
        short_interset_value = short_interest_scraper(ticker.symbol) #get short interest value 
        if short_interset_value >=30: 
            Alert.objects.create(ticker=ticker,strategy='Short Interest',result_value=short_interset_value)




from Alerts.models import Ticker , Result ,  Alert
import requests
from datetime import  timedelta
import time
from datetime import date as dt , datetime
from celery import shared_task
from .TwitterScraper import twitter_scraper
from .RedditScraper import main
from .ShortIntrestScraper  import short_interest_scraper
from Alerts.OptionsScraper import earning_scraping
from celery.exceptions import SoftTimeLimitExceeded
from django.db.models import Q
import redis
from django.core.cache import cache
from .consumers import WebSocketConsumer
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
# def get_tickers():
#     redis_client.set("tickers")

def get_cached_queryset():
    queryset = cache.get("tickerlist")
    if not queryset:
        queryset = Ticker.objects.all()
        cache.set("tickerlist", queryset, timeout=86400)
    return queryset

## task for Earning strategy ##
def Earnings(duration):
    # value = redis_client.get('tickers')
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    ## token for request on current IV ##
    token = 'a4c1971d-fbd2-417e-a62d-9b990309a3ce'  
    ## today date ##
    today = dt.today()
    thatday = today + timedelta(days=duration) ## date after period time ##
    # print(thatday)
    ## for Authentication on request for current IV ##
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'  # Optional, depending on the API requirements
    }
    ## response of the api ##
    response = requests.get(f'https://financialmodelingprep.com/api/v3/earning_calendar?from={thatday}&to={thatday}&apikey={api_key}')
    if response.json() != []:
        tickers = get_cached_queryset()
        for slice in response.json():
            Estimated_EPS = slice['epsEstimated']
            dotted_ticker = '.' in slice['symbol']
            if not dotted_ticker:
                if Estimated_EPS != None :
                    symbol = slice['symbol']
                    try:
                        ticker2 = next((ticker for ticker in tickers if ticker.symbol == symbol), None)
                        time = slice['time']
                        Estimated_Revenue = slice['revenueEstimated']
                        if Estimated_Revenue != None:
                            Expected_Moves = earning_scraping(ticker2.symbol)
                            current_IV = requests.get(f'https://api.unusualwhales.com/api/stock/{symbol}/option-contracts',headers=headers).json()['data'][0]['implied_volatility']
                            alert = Alert.objects.create(ticker=ticker2 ,strategy= 'Earning', 
                                        time_frame = str(duration) , Estimated_Revenue = Estimated_Revenue, current_IV=current_IV,
                                        Estimated_EPS = Estimated_EPS , Expected_Moves=Expected_Moves , earning_time=time)
                            WebSocketConsumer.send_new_alert(alert)
                    except:
                        continue

## method to get data of ticker by api ##
def getIndicator(ticker , timespan , type):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type={type}&period=14&apikey={api_key}')
    return data.json()

def MajorSupport(timespan):
    ## check the limitation number of days accourding to timespan ##
    if timespan == '1day' or timespan == '4hour':
        limit_number_days = 30
    elif timespan == '1hour':
        limit_number_days = 7

    ## get the limitation date ##
    limit_date  = datetime.today() - timedelta(days=limit_number_days)
    # print(limit_date)
    # print(type(limit_date))
    tickers = get_cached_queryset()
    is_cached = True
    previous_rsi_alerts = cache.get(f"MajorSupport_{timespan}")
    if not previous_rsi_alerts:
        is_cached = False
    major_data = []
    for ticker in tickers:
        counter = 0 ## number of candies that has the same range value 
        largest_number= 0
        smallest_number= 1000000000000000000
        results = getIndicator(ticker=ticker.symbol , timespan=timespan , type='rsi')
        if results!= []:
            try:
                for result in results[1:]:
                    ## convert string date to date type ##
                    date_of_result = datetime.strptime(result['date'] , "%Y-%m-%d %H:%M:%S")
                    # print(date_of_result)
                    # print(type(date_of_result))
                    ## check condition of strategy (range of price and date) ## 
                    if (
                        ((abs(results[0]['open']-result['open']) <= 0.8) or 
                        (abs(results[0]['open']-result['close']) <= 0.8) or 
                        (abs(results[0]['close']-result['open']) <= 0.8) or 
                        (abs(results[0]['close']-result['open']) <= 0.8)) and
                        (date_of_result >= limit_date)
                    ):
                        # print("success")
                        counter += 1
                        largest_number = max(results[0]['open'],results[0]['close'],result['open'],result['close'] , largest_number)
                        smallest_number = min(results[0]['open'],results[0]['close'],result['open'],result['close'] , smallest_number)
                if counter >= 5:
                    # print("counter="+str(counter))
                    range_of_price = (largest_number+smallest_number)/2
                    # print("range of price="+str(range_of_price))
                    alert = Alert.objects.create(ticker=ticker,strategy='Major Support',time_frame=timespan,result_value=range_of_price , Estimated_Revenue=counter)
                    WebSocketConsumer.send_new_alert(alert)
                    break
            ## if there is any exception ##
            except BaseException:
                continue

## tasks for MajorSupport strategy ##
# for time frame 1 day #
@shared_task(queue="Main")
def MajorSupport_1day():
    MajorSupport('1day')

# for time frame 4 hour #
@shared_task(queue="Main")
def MajorSupport_4hour():
    MajorSupport('4hour')

# for time frame 1 hour #
@shared_task(queue="Main")
def MajorSupport_1hour():
    MajorSupport('1hour')

## rsi function ##
## rsi function ##
def rsi(timespan):
    tickers = get_cached_queryset()
    for ticker in tickers:
        risk_level = None
        ticker_price = None
        result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='rsi')
        if result != []:
            try:
                rsi_value = result[0]['rsi']
                ticker_price = result[0]['close']
                previous_value = result[1]['rsi']
                previous_price = result[1]['close']
            except BaseException:
                continue
            # to calculate results of strategy success according to current price ##
            if (
                (previous_value > 70 and previous_price > ticker_price) or 
                (previous_value < 30 and previous_price < ticker_price)
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
            # Creating the Alert object and sending it to the websocket
            if rsi_value > 70:
                risk_level = 'Bearish'
            if rsi_value < 30:
                risk_level = 'Bullish'
            if risk_level != None:
                try:
                    alert = Alert.objects.create(ticker=ticker , strategy= 'RSI' ,time_frame=timespan ,risk_level=risk_level , result_value = rsi_value , current_price = ticker_price)
                    alert.save()  
                    WebSocketConsumer.send_new_alert(alert)
                except:
                    continue


## ema function ##
def ema(timespan):
    # print("getting EMA")
    tickers = get_cached_queryset()
    for ticker in tickers:
        result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='ema')
        if result != []:
            try:
                ema_value = result[0]['ema']
                current_price = result[0]['close']
                old_price = result[1]['close']
                old_ema = result[1]['ema']
                older_price = result[2]['close']
            except BaseException:
                continue
            # to calculate results of strategy success according to current price and the old prices #
            if (
                (old_ema < old_price and old_ema > older_price and current_price < old_price) or 
                (old_ema > old_price and old_ema < older_price and current_price > old_price)
                ):
                result = Result.objects.get(strategy='EMA',time_frame=timespan)
                result.success += 1
                result.total += 1
                result.result_value = (result.success / result.total)*100
                result.save()
            else:
                result = Result.objects.get(strategy='EMA',time_frame=timespan)
                result.total += 1
                result.result_value = (result.success / result.total)*100
                result.save()
            # Creating the Alert object and sending it to the websocket
            risk_level = None
            if ema_value < current_price and ema_value > old_price:
                risk_level = 'Bullish'
            if ema_value > current_price and ema_value < old_price:
                risk_level = 'Bearish'
            if risk_level != None:   
                try:
                    alert = Alert.objects.create(ticker=ticker , strategy= 'EMA' ,time_frame=timespan ,risk_level=risk_level , result_value = ema_value, current_price=current_price)
                    alert.save()
                    WebSocketConsumer.send_new_alert(alert)
                except:
                    continue


## endpint for RSI 4 hours ##
@shared_task(queue="Main")
def RSI_4hour():
    rsi(timespan='4hour')
    
## endpint for RSI 1day ##
@shared_task(queue="Main")
def RSI_1day():
    rsi(timespan='1day')

## view for EMA  1day ##
@shared_task(queue="Main")
def EMA_DAY():
    ema(timespan='1day')
## view for EMA  4hour  ##
@shared_task(queue="Main")
def EMA_4HOUR(): 
    ema(timespan='4hour')

## view for EMA  1hour ##
@shared_task(queue="Main")
def EMA_1HOUR():
    ema(timespan='1hour')


@shared_task(queue="Twitter")
def twitter_scrap():
    twitter_scraper()

## for web scraping ##
# def web_scraping_alerts():
#     # twitter_scraper_dict = {}
#     #######################################
#     # all_tickers = get_cached_queryset()
#     # print("before redit")
#     # reddit_scraper_dict = main(all_tickers)
#     reddit_scraper_dict = {}
#     # print("after redit")
#     # print(reddit_scraper_dict)
#     twitter_scraper_dict = twitter_scraper()
#     print(twitter_scraper_dict)
#     ## get the tallest length of dictionary ##
#     test_dict = {
#         len(twitter_scraper_dict):twitter_scraper_dict,
#         len(reddit_scraper_dict):reddit_scraper_dict}
#     max_length = max(list(test_dict.keys())[0],list(test_dict.keys())[1])
#     min_length = min(list(test_dict.keys())[0],list(test_dict.keys())[1])
#     #### combine two dictionary ####
#     combined_dictionary = {**twitter_scraper_dict,**reddit_scraper_dict}
#     ## looping to sum values of common keys ##
#     for key in test_dict[max_length]:
#         if key in test_dict[min_length]:
#             combined_dictionary[key] = twitter_scraper_dict[key] + reddit_scraper_dict[key]
#     ## looping in the combined dictionary ###
#     for key , value in combined_dictionary.items():
#         if value >=3 :
#             ticker = Ticker.objects.get(symbol=key)
#             Alert.objects.create(ticker= ticker, strategy= "People's Opinion", result_value= value )




## task for Relative Volume strategy ##
@shared_task(queue="Main")
def Relative_Volume():
    tickers = get_cached_queryset()
    is_cached = True
    previous_volume_alerts = cache.get('relative_volume_alerts')
    if not previous_volume_alerts:
        is_cached = False
        volume_alerts = []
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    for ticker in tickers:
        response = requests.get(f'https://financialmodelingprep.com/api/v3/quote/{ticker.symbol}?apikey={api_key}').json()
        try:
            volume = response[0]['volume']
            avgVolume = response[0]['avgVolume']
            current_price = response[0]['price']
        except BaseException:
            continue
        if response != []:
            if is_cached:
                for previous_alert in previous_volume_alerts:
                    if previous_alert.ticker.symbol == ticker.symbol:
                        if previous_alert.current_price > current_price:
                            result = Result.objects.get(strategy='Relative Volume')
                            result.success += 1
                            result.total += 1
                            result.result_value = (result.success / result.total)*100
                            result.save()
                        else:
                            result = Result.objects.get(strategy='Relative Volume')
                            result.total += 1
                            result.result_value = (result.success / result.total)*100
                            result.save()
                        previous_volume_alerts.remove(previous_alert)
                        break                        
                if volume > avgVolume and avgVolume != 0:
                    value2 = int(volume) -int(avgVolume)
                    value = (int(value2)/int(avgVolume)) * 100
                    # now = datetime.now()
                    # one_hour_ago = now - timedelta(hours=1)
                    try:
                        alert = Alert.objects.create(ticker=ticker ,strategy='Relative Volume' ,result_value=value ,risk_level= 'overbought average', current_price=current_price)
                        alert.save()
                        WebSocketConsumer.send_new_alert(alert)
                        volume_alerts.append(alert)
                    except:
                        pass
    if is_cached:
        cache.delete("relative_volume_alerts")
    ### combine new alerts with the cached data ###
    if previous_volume_alerts != [] and previous_volume_alerts != None:
        previous_volume_alerts = volume_alerts.extend(previous_volume_alerts)
        cache.set('relative_volume_alerts', previous_volume_alerts, timeout=86400*2)
    elif volume_alerts != []:
        cache.set('relative_volume_alerts', volume_alerts, timeout=86400*2)

### task for 13F ###
list_of_CIK = ['0001067983']
@shared_task(queue="Main")
def get_13f():
    # print("getting 13F")
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
            tickers = get_cached_queryset()
            is_cached = True
            previous_13F_alerts = cache.get(f"13F")
            for slice in response:
                changeInSharesNumber = slice['changeInSharesNumber']
                name = slice['investorName']
                symbol = slice['symbol']
                ticker = next((ticker for ticker in tickers if ticker.symbol == symbol), None)
                ticker_data = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={api_key_fmd}').json()
                price = ticker_data[0]['price']
                amount_of_investment = float(price) * abs(changeInSharesNumber)
                if amount_of_investment >= 1000000:
                    if changeInSharesNumber > 0 :
                        transaction = 'bought'
                    else:
                        transaction = 'sold'
                        alert = Alert.objects.create(investor_name = name , transaction_type = transaction , 
                                             shares_quantity = changeInSharesNumber , ticker= ticker ,
                                             ticker_price=price , amount_of_investment=amount_of_investment)
                        alert.save()
                        WebSocketConsumer.send_new_alert(alert)


## Earning strategy in 15 days ##
@shared_task(queue="Main")
def earning15():
    Earnings(15)

## Earning strategy in 30 days ##
@shared_task(queue="Main")
def earning30():
    Earnings(30)

# Insider Buyers Strategy
@shared_task(queue="Main")
def Insider_Buyer():
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    tickers = get_cached_queryset()
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)
    for ticker in tickers:
        response = requests.get(f'https://financialmodelingprep.com/api/v4/insider-trading?symbol={ticker.symbol}&page=0&apikey={api_key}').json()
        if response != []:
            for i in range(len(response)):
                filing_date_str = response[i]['filingDate']
                filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d %H:%M:%S")
                # checking if the date is within the range of the current date range
                if now.date() == filing_date.date() and now.hour == filing_date.hour:
                    # checking the transaction type if it is either sales or purchases if it is another type then pass 
                    if response[i]["transactionType"] == 'S-Sale'  or response[i]["transactionType"] == 'P-Purchase':
                        # the "price" means that each share of the common stock was sold or bought for this price and it is not comparable with the closed price.
                        try:
                            alert = Alert.objects.create(ticker=ticker, strategy='Insider Buyer', ticker_price=response[i]['price'],
                                        transaction_date=response[i]['transactionDate'], investor_name=response[i]['reportingName'],
                                        job_title=response[i]["typeOfOwner"], shares_quantity=response[i]["securitiesTransacted"],
                                        transaction_type=response[i]["transactionType"], filling_date=str(filing_date_str))
                            alert.save()
                            WebSocketConsumer.send_new_alert(alert)
                        except:
                            continue
                
                elif now.date() == filing_date and  one_hour_ago <= filing_date < now:
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

## task for Unusual Option Buys strategy ##
@shared_task(queue="Main")
def Unusual_Option_Buys():
    tickers = get_cached_queryset()
    token = 'a4c1971d-fbd2-417e-a62d-9b990309a3ce'  
    ## for Authentication on request ##
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'  # Optional, depending on the API requirements
    }
    ticker_count = 0
    ## looping on tickers ##
    for ticker in tickers:
        ticker_count += 1
        if ticker_count % 119 == 0:
            time.sleep(40)
        response = requests.get(
            f'https://api.unusualwhales.com/api/stock/{ticker.symbol}/options-volume',
            headers=headers
        ).json()
        
        try:
            ## to get avg of call transaction ##
            avg_30_day_call_volume = response['data'][0]['avg_30_day_call_volume']
            ## average number of put transaction ##
            avg_30_day_put_volume = response['data'][0]['avg_30_day_put_volume']
            # date = response['data'][0]['date']
            ### get all contracts for each ticker ###    
            contract_options = requests.get(f'https://api.unusualwhales.com/api/stock/{ticker.symbol}/option-contracts',headers=headers).json()['data']
            try:
                ## looping on each contract ##
                for contract in contract_options:
                    volume = contract['volume']
                    contract_id = contract['option_symbol']
                    if contract_id[-9] == 'C':
                        if float(volume) > float(avg_30_day_call_volume):
                            alert = Alert.objects.create(ticker=ticker 
                                ,strategy='Unusual Option Buys' ,time_frame='1day' ,result_value=volume, 
                                risk_level= 'Call' ,investor_name=contract_id , amount_of_investment= avg_30_day_call_volume)
                            WebSocketConsumer.send_new_alert(alert)
                    else:
                        if float(volume) > float(avg_30_day_put_volume):
                            try:
                                alert = Alert.objects.create(ticker=ticker 
                                    ,strategy='Unusual Option Buys' ,time_frame='1day' ,result_value=volume, 
                                    risk_level= 'Put' ,investor_name=contract_id , amount_of_investment= avg_30_day_put_volume)
                                alert.save()
                                WebSocketConsumer.send_new_alert(alert)
                            except:
                                continue
            except BaseException:
                continue
        except BaseException :
            continue

# Short Interest Strategy
@shared_task(queue="Main")
def Short_Interset():
    tickers = get_cached_queryset()
    result = Result.objects.get(strategy='Short Interest')
    symbols = short_interest_scraper(tickers)
    if symbols != []:
        for symbol in symbols:
            result = getIndicator(ticker=symbol , timespan='1hour' , type='rsi')
            price = result[0]['close']
            old_price = result[1]['close']
            if old_price > price:    
                result.success += 1
                result.total += 1
            else:
                result = result
                result.total += 1
        result.result_value = (result.success / result.total)*100
        result.save()
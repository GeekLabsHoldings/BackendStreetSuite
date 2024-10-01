from Alerts.models import Ticker , Result ,  Alert
from .Scraping.TwitterScraper import twitter_scraper
from .Scraping.ShortIntrestScraper  import short_interest_scraper
from .Scraping.EarningsScraper import earning_scraping
from .Scraping.InsiderBuyerScraper import insider_buyers_scraper
import requests, time
from datetime import  timedelta
from datetime import date as dt , datetime
from celery import shared_task, chain, group , chord
from .consumers import WebSocketConsumer
from Payment.tasks import upgrade_to_monthly
from django.core.cache import cache
from collections import defaultdict
##########################################
from .Strategies.RSI import GetRSIStrategy
from .Strategies.MajorSupport import GetMajorSupport
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
    print("response",response.json())
    if response.json() != []:
        print("RESPONSE != []")
        tickers = get_cached_queryset()
        for slice in response.json():
            Estimated_EPS = slice['epsEstimated']
            dotted_ticker = '.' in slice['symbol']
            if not dotted_ticker:
                if Estimated_EPS != None :
                    symbol = slice['symbol']
                    print("ticker: ",symbol)
                    print("Estimated_EPS: ",Estimated_EPS)
                    try:
                        ticker2 = next((ticker for ticker in tickers if ticker.symbol == symbol), None)
                        print('ticker value: ',ticker2)
                        time = slice['time']
                        print('time: ',time)
                        Estimated_Revenue = slice['revenueEstimated']
                        print('Estimated_Revenue: ',Estimated_Revenue)
                        if Estimated_Revenue != None:
                            Expected_Moves = earning_scraping(ticker2.symbol)
                            print('Expected_Moves: ',Expected_Moves)
                            current_IV = requests.get(f'https://api.unusualwhales.com/api/stock/{symbol}/option-contracts',headers=headers).json()['data'][0]['implied_volatility']
                            print('current_IV: ',current_IV)
                            alert = Alert.objects.create(ticker=ticker2 ,strategy= 'Earning', 
                                        time_frame = str(duration) , Estimated_Revenue = Estimated_Revenue, current_IV=current_IV,
                                        Estimated_EPS = Estimated_EPS , Expected_Moves=Expected_Moves , earning_time=time)
                            alert.save()
                            print("new alert")
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
    print(limit_date)
    # print(type(limit_date))
    tickers = get_cached_queryset()
    is_cached = True
    # previous_rsi_alerts = cache.get(f"MajorSupport_{timespan}")
    # if not previous_rsi_alerts:
    #     is_cached = False
    major_data = []
    i =0
    for ticker in tickers[:100]:
        i += 1
        print(f'Major {timespan} {i}')
        counter = 0 ## number of candies that has the same range value 
        largest_number= 0
        smallest_number= 1000000000000000000
        results = getIndicator(ticker=ticker.symbol , timespan=timespan , type='rsi')
        if results!= []:
            print("result not []")
            try:
                for result in results[1:]:
                    ## convert string date to date type ##
                    date_of_result = datetime.strptime(result['date'] , "%Y-%m-%d %H:%M:%S")
                    # print(date_of_result)
                    # print(type(date_of_result))
                    if date_of_result >= limit_date:
                        pass
                    ## check condition of strategy (range of price and date) ## 
                    if (
                        ((abs(results[0]['open']-result['open']) <= 0.8) or 
                        (abs(results[0]['open']-result['close']) <= 0.8) or 
                        (abs(results[0]['close']-result['open']) <= 0.8) or 
                        (abs(results[0]['close']-result['open']) <= 0.8))
                        
                    ):
                       
                        counter += 1
                        largest_number = max(results[0]['open'],results[0]['close'],result['open'],result['close'] , largest_number)
                        smallest_number = min(results[0]['open'],results[0]['close'],result['open'],result['close'] , smallest_number)
                if counter >= 5:
                    # print("yes")
                    # print("counter="+str(counter))
                    range_of_price = (largest_number+smallest_number)/2
                    # print("range of price="+str(range_of_price))
                    alert = Alert.objects.create(ticker=ticker,strategy='Major Support',time_frame=timespan,result_value=range_of_price , Estimated_Revenue=counter)
                    alert.save()
                    print("newss")
                    # caching = alerts_today(strategy='major',key_name=timespan).copy()
                    # caching[f'{ticker.symbol}'].append({"strategy":"Major Support","value":range_of_price,"risk level":"none"})
                    # # Update the cache with the modified queryset
                    # cache.set(f"TodayAlerts_{timespan}", caching, timeout=86400)
                    # if ticker.symbol not in caching.keys():
                    #     caching[f'{ticker.symbol}'] = 
                    # else:

                    WebSocketConsumer.send_new_alert(alert)
                    break
            ## if there is any exception ##
            except Exception as e:
                print({"Error" : e })
                continue

## tasks for MajorSupport strategy ##
# for time frame 1 day #
@shared_task(queue='Main')
def MajorSupport_1day():
    GetMajorSupport(timespan='1day')

# for time frame 4 hour #
@shared_task(queue='celery_4hour')
def MajorSupport_4hour():
    GetMajorSupport(timespan='4hour')

# for time frame 1 hour #
@shared_task(queue='celery_1hour')
def MajorSupport_1hour():
    GetMajorSupport(timespan='1hour')

## rsi function ##
def rsi(ticker,timespan):
    print(ticker.symbol)
    ## initialize results parameters ##
    result_strategy = Result.objects.get(strategy='RSI',time_frame=timespan)
    result_success = 0
    result_total = 0
    # for ticker in tickers[800:900]:
    risk_level = None
    ticker_price = None
    result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='rsi')
    if result != []:
        print(f"rsi {ticker.symbol}")
        try:
            rsi_value = result[0]['rsi']
            ticker_price = result[0]['close']
            previous_value = result[1]['rsi']
            previous_price = result[1]['close']
        except BaseException:
            return None
        # to calculate results of strategy success according to current price ##
        if (
            (previous_value > 70 and previous_price > ticker_price) or 
            (previous_value < 30 and previous_price < ticker_price)
        ):
            result_success += 1
            result_total += 1
        else:
            result_total += 1
        # Creating the Alert object and sending it to the websocket
        if rsi_value > 70:
            risk_level = 'Bearish'
        if rsi_value < 30:
            risk_level = 'Bullish'
        if risk_level != None:
            try:
                print(f"rsi:{rsi_value}")
                alert = Alert.objects.create(ticker=ticker , strategy= 'RSI' ,time_frame=timespan ,risk_level=risk_level , result_value = rsi_value , current_price = ticker_price)
                alert.save()  
                print("rsi created")
                # Update the cache with the modified queryset
                WebSocketConsumer.send_new_alert(alert)
                return alert
                
            except:
                return None
    ## calculate the total result of strategy ##
    result_strategy.success += result_success
    result_strategy.total += result_total
    result_strategy.save()


## ema function ##
def ema(ticker,timespan):
    print(f"ema {ticker.symbol}")
    ## initialize results parameters ##
    result_strategy = Result.objects.get(strategy='EMA',time_frame=timespan)
    result_success = 0
    result_total = 0
    i = 0
    # caching = alerts_today(strategy="ema",key_name=timespan)
    # for ticker in tickers[800:900]:
    i += 1
    # print(f"EMA {timespan} {i}")
    result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='ema')
    if result != []:
        try:
            ema_value = result[0]['ema']
            current_price = result[0]['close']
            old_price = result[1]['close']
            old_ema = result[1]['ema']
            older_price = result[2]['close']
        except BaseException:
            return None
        # to calculate results of strategy success according to current price and the old prices #
        if (
            (old_ema < old_price and old_ema > older_price and current_price < old_price) or 
            (old_ema > old_price and old_ema < older_price and current_price > old_price)
            ):
            result_success += 1
            result_total += 1
        else:
            result_total += 1
        # Creating the Alert object and sending it to the websocket
        risk_level = None
        if ema_value < current_price and ema_value > old_price:
            risk_level = 'Bullish'
        if ema_value > current_price and ema_value < old_price:
            risk_level = 'Bearish'
        if risk_level != None:   
            try: 
                print(f"ema:{ema_value}")
                # caching[f'{ticker.symbol}'].append({"strategy":"EMA","value":ema_value,"risk level":risk_level})
                alert = Alert.objects.create(ticker=ticker , strategy= 'EMA' ,time_frame=timespan ,risk_level=risk_level , result_value = ema_value, current_price=current_price)
                alert.save()
                print("ema created")
                # Update the cache with the modified queryset
                WebSocketConsumer.send_new_alert(alert)
                return alert
            except:
                return None
    result_strategy.success += result_success
    result_strategy.total += result_total
    result_strategy.save()


## endpint for RSI 4 hours ##
@shared_task(queue='celery_4hour')
def RSI_4hour():
    GetRSIStrategy(timespan='4hour')
    
## endpint for RSI 1day ##
@shared_task(queue='Main')
def RSI_1day():
    GetRSIStrategy(timespan='1day')

# ## view for EMA  1day ##
# @shared_task(queue='Main')
# def EMA_DAY():
#     ema(timespan='1day')
# ## view for EMA  4hour  ##
# @shared_task(queue='celery_4hour')
# def EMA_4HOUR(): 
#     ema(timespan='4hour')

# ## view for EMA  1hour ##
# @shared_task(queue='celery_1hour')
# def EMA_1HOUR():
#     ema(timespan='1hour')


@shared_task(queue="Twitter")
def twitter_scrap():
    twitter_scraper()

## task for Relative Volume strategy ##
@shared_task()
def Relative_Volume():
    tickers = get_cached_queryset()
    is_cached = True
    previous_volume_alerts = cache.get('relative_volume_alerts')
    volume_alerts = []
    if not previous_volume_alerts:
        is_cached = False
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    ## initialize the parameter to calculate result ##
    result_success = 0
    result_total = 0
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
                            result_success += 1
                            result_total += 1
                        else:
                            result_total += 1
                        previous_volume_alerts.remove(previous_alert)
                        break                        
            if volume > avgVolume and avgVolume != 0:
                value2 = int(volume) -int(avgVolume)
                value = (int(value2)/int(avgVolume)) * 100
                try:
                    alert = Alert.objects.create(ticker=ticker ,strategy='Relative Volume' ,result_value=value ,risk_level= 'overbought average', current_price=current_price)
                    alert.save()
                    WebSocketConsumer.send_new_alert(alert)
                    volume_alerts.append(alert)
                except:
                    pass
    ## append the success and total time of result of strategy success ##
    result = Result.objects.get(strategy='Relative Volume')
    result.success += result_success
    result.total += result_total
    result.save()
    ## check if cachedd ##
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
@shared_task()
def get_13f():
    api_key_fmd = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2' 
    day = str(dt.today().date())
    strategy = '13F strategy'
    for cik in list_of_CIK:
        response = requests.get(f'https://financialmodelingprep.com/api/v4/institutional-ownership/portfolio-holdings?date={day}&cik={cik}&page=0&apikey={api_key_fmd}').json()
        if response != []:
            tickers = get_cached_queryset()
            is_cached = True
            previous_13F_alerts = cache.get(f"13F")
            for slice in response:
                changeInSharesNumber = slice['changeInSharesNumber']
                name = slice['investorName']
                symbol = slice['symbol']
                ticker = next((ticker for ticker in tickers if ticker.symbol == symbol), None)
                if ticker != None:
                    ticker_data = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={api_key_fmd}').json()
                    price = ticker_data[0]['price']
                    amount_of_investment = float(price) * abs(changeInSharesNumber)
                    if amount_of_investment >= 1000000:
                        if changeInSharesNumber > 0 :
                            transaction = 'bought'
                        else:
                            transaction = 'sold'
                        try:
                            shares_quantity = abs(changeInSharesNumber)
                            alert = Alert.objects.create(investor_name = name , transaction_type = transaction , strategy=strategy,
                                                shares_quantity = shares_quantity , ticker= ticker ,
                                                ticker_price=price , amount_of_investment=amount_of_investment)
                            alert.save()
                            WebSocketConsumer.send_new_alert(alert)
                        except:
                            continue

## Earning strategy in 15 days ##
@shared_task()
def earning15():
    Earnings(15)

## Earning strategy in 30 days ##
@shared_task()
def earning30():
    Earnings(30)

# Insider Buyers Strategy
@shared_task(queue='celery_timeless')
def Insider_Buyer(*args, **kwargs):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    symbols = insider_buyers_scraper()
    tickers = Ticker.objects.filter(symbol__in=symbols)
    now = datetime.now()
    for ticker in tickers: 
        print(f'insider buyer {ticker.symbol}')
        response = requests.get(f'https://financialmodelingprep.com/api/v4/insider-trading?symbol={ticker.symbol}&page=0&apikey={api_key}').json()
        if response != []:
            for i in range(len(response)):
                filing_date_str = response[i]['filingDate']
                filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d %H:%M:%S")
                # checking if the date is within the range of the current date range
                if now.date() == filing_date.date():
                    # checking the transaction type if it is either sales or purchases if it is another type then pass 
                    if response[i]["transactionType"] == 'S-Sale'  or response[i]["transactionType"] == 'P-Purchase':
                        # the "price" means that each share of the common stock was sold or bought for this price and it is not comparable with the closed price.
                        print(f"alert in {ticker.symbol}")
                        try:
                            alert = Alert.objects.create(ticker=ticker, strategy='Insider Buyer', ticker_price=response[i]['price'],
                                        transaction_date=response[i]['transactionDate'], investor_name=response[i]['reportingName'],
                                        job_title=response[i]["typeOfOwner"], shares_quantity=response[i]["securitiesTransacted"],
                                        transaction_type=response[i]["transactionType"], filling_date=str(filing_date_str))
                            alert.save()
                            WebSocketConsumer.send_new_alert(alert)
                        except:
                            continue
                elif now.date() == filing_date:
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
@shared_task(queue='celery_1hour')
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
    for ticker in tickers[:100]:
        ticker_count += 1
        print(f"unusiual options {ticker_count}")
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
                            alert.save()
                            # caching = alerts_today(key_name="1day")
                            # caching[f'{ticker.symbol}'].append({"strategy":"Major Support","value":volume,"risk level":"Bearish"})
                            WebSocketConsumer.send_new_alert(alert)
                    else:
                        if float(volume) > float(avg_30_day_put_volume):
                            try:
                                alert = Alert.objects.create(ticker=ticker 
                                    ,strategy='Unusual Option Buys' ,time_frame='1day' ,result_value=volume, 
                                    risk_level= 'Put' ,investor_name=contract_id , amount_of_investment= avg_30_day_put_volume)
                                alert.save()
                                # caching = alerts_today(key_name="1day")
                                # caching[f'{ticker.symbol}'].append({"strategy":"Major Support","value":volume,"risk level":"Bullish"})
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
    short_interest_scraper()

######## grouping tasks according to time frame ###########
## time frame 1 day ##
@shared_task(queue='celery_timeless')
def timeless_tasks():
    chain(Insider_Buyer.s(), Short_Interset.s())()

## method to print caching ##
# def print_caching(*args,**kwargs):
#     caching_rsi = cache.get("TodayAlerts_rsi_1day")
#     caching_ema = cache.get("TodayAlerts_ema_1day")
#     print("yes yes yes yes")
#     print(f"caching rsi Before {caching_rsi}") 
#     print(f"caching ema Before {caching_ema}") 
#     print('rsi',len(caching_rsi))
#     print('ema',len(caching_ema))
#     if len(caching_rsi) > len(caching_ema):
#         taller = caching_rsi
#         smaller = caching_ema
#     else:
#         taller = caching_ema
#         smaller = caching_rsi
#     for key , value in taller.items():
#         smaller[key].extend(value)
#     print("after compination")
#     print("smaller",smaller)
#     # caching_rsi.clear()
#     # caching_ema.clear()
#     # print(f"caching rsi After clear {caching_rsi}")
#     # print(f"caching ema After clear {caching_ema}")
#     return "done"

######## COMMON METHOD FOR COMMON ALERTS #########
def common(timeframe):
    all_tickers = get_cached_queryset()
    print("got tickers")
    for ticker in all_tickers:
        print(ticker.symbol)
        ## initialize list of alerts that common on the same ticker ##
        list_alerts = []
        ## initialize list of applied functions for the time frame ##
        # applied_functions = [rsi(ticker=ticker, timespan='1day'),ema(ticker=ticker, timespan='1day')]
        applied_functions = [rsi,ema]
        for function in applied_functions:
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
            alert = Alert.objects.create(ticker=ticker ,strategy='Common Alert', investor_name=message ,timespan=timeframe )
            alert.save()
            WebSocketConsumer.send_new_alert(alert)


@shared_task(queue='Main')
def tasks_1day():
    common(timeframe='1day')
            
@shared_task(queue='celery_1hour')
def tasks_1hour():
    common(timeframe='1hour')
            
@shared_task(queue='celery_4hour')
def tasks_4hour():
    common(timeframe='4hour')
            
            
# ## time frame 1 hour ##
# @shared_task(queue='celery_1hour')
# def tasks_1hour():
#     tasks = group(EMA_1HOUR.s(),MajorSupport_1hour.s())
#     tasks.apply_async()
# ## time frame 4 hour ##
# @shared_task(queue='celery_4hour')
# def tasks_4hour():
#     tasks = group(RSI_4hour.s(),EMA_4HOUR.s(),MajorSupport_4hour.s())
#     tasks.apply_async()

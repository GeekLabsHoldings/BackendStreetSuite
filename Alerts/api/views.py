from Alerts.models import Alert , Result , Industry
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import ListAPIView
from .serializer import AlertSerializer
from .paginations import AlertPAgination
from .filters import AlertFilters
from rest_framework.decorators import api_view
from Alerts.Scraping.ShortIntrestScraper import short_interest_scraper as shy
from Alerts.models import Ticker
from rest_framework.response import Response
from Alerts.Scraping.EarningsScraper import earning_scraping
from datetime import timedelta , date
import requests
from Alerts.tasks import MajorSupport , getIndicator
from datetime import datetime as dt
from django.core.cache import cache
from Alerts.tasks import  earning30 , MajorSupport 
from Alerts.tasks import  rsi as RS
from Alerts.tasks import ema as EM
from Alerts.Scraping.TwitterScraper import twitter_scraper
from Alerts.Scraping.RedditScraper import Reddit_API_Response
from Alerts.tasks import earning15 , earning30 , MajorSupport
from Alerts.consumers import WebSocketConsumer
from celery import group , chord
from  datetime import datetime
import time
#########################################################
################ Reddit Dependencies ####################
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import pytz
import re
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import csv
#########################################################

## test earning ##
@api_view(['GET'])
def earny(request):
    earning30()
    return Response({"message":"successed!"})
## test major ##
@api_view(['GET'])
def mj(request):
    MajorSupport('1day')
    return Response({"message":"successed!"})

## get all tickers in cache ##
def get_cached_queryset():
    queryset = cache.get("tickerlist")
    if not queryset:
        queryset = Ticker.objects.all()
        cache.set("tickerlist", queryset, timeout=86400)
    return queryset

## method to get all symbols ##
def get_symbols():
    all_tickers = get_cached_queryset()
    all_symbols = [ticker.symbol for ticker in all_tickers]
    return all_symbols

## list of symbols ##
our_symbols = get_symbols()

## view list alerts ###
class AlertListView(ListAPIView):
    # permission_classes = [HasActiveSubscription]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    pagination_class = AlertPAgination
    filterset_class = AlertFilters
    search_fields = ['ticker__symbol']
    queryset = Alert.objects.all().order_by('-date','-time')
    serializer_class = AlertSerializer


@api_view(['GET'])
def MajorSupportTEST(request):
    MajorSupport('1hour')
    return Response({"message":"done"})

def get_cached_queryset():
    queryset = cache.get("tickerlist")
    if not queryset:
        print("getting ticker for web scraping")
        queryset = Ticker.objects.all()
        cache.set("tickerlist", queryset, timeout=86400)
    return queryset

@api_view(['GET'])
def Earnings(request):
    # value = redis_client.get('tickers')
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    ## token for request on currunt IV ##
    token = 'a4c1971d-fbd2-417e-a62d-9b990309a3ce'  
    ## today date ##
    today = dt.today()
    thatday = today + timedelta(days=15) ## date after period time ##
    print(thatday)
    ## for Authentication on request for currunt IV ##
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'  # Optional, depending on the API requirements
    }
    ## response of the api ##
    response = requests.get(f'https://financialmodelingprep.com/api/v3/earning_calendar?from={thatday}&to={thatday}&apikey={api_key}')
    if response.json() != []:
        print(len(response.json()))
        for slice in response.json()[:1000]:
            Estimated_EPS = slice['epsEstimated']
            dotted_ticker = '.' in slice['symbol']
            if not dotted_ticker and Estimated_EPS != None :
                ticker = slice['symbol']
                print(ticker)
                try:
                    ticker2 = Ticker.objects.get(symbol=ticker)
                    time = slice['time']
                    if time != '--':
                        print('time'+time)
                        Estimated_Revenue = slice['revenueEstimated']
                        print('Estimated_Revenue')
                        print(Estimated_Revenue) 
                        # if Estimated_Revenue != None:
                        Expected_Moves = earning_scraping(ticker) 
                        current_IV = requests.get(f'https://api.unusualwhales.com/api/stock/{ticker}/option-contracts',headers=headers).json()['data'][0]['implied_volatility']
                        print('current_IV')
                        print(current_IV)
                        Alert.objects.create(ticker=ticker2 ,strategy= 'Earning', 
                                    time_frame = '15' , Estimated_Revenue = Estimated_Revenue, current_IV= current_IV ,
                                    Estimated_EPS = Estimated_EPS , Expected_Moves=Expected_Moves , earning_time=time)
                except:
                        continue

    return Response({"gg":"hh"})

## rsi function ##
def rsi(timespan):
    tickers = get_cached_queryset()
    is_cached = True
    previous_rsi_alerts = cache.get(f"RSI_{timespan}")
    print(previous_rsi_alerts)
    if not previous_rsi_alerts:
        is_cached = False
    rsi_data = []
    for ticker in tickers:
        risk_level = None
        ticker_price = None
        result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='rsi')
        if result != []:
            try:
                rsi_value = result[0]['rsi']
                ticker_price = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{ticker.symbol}?apikey=juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2').json()[0]['price']
            except BaseException:
                continue
             ## to calculate results of strategy successful accourding to current price ##
            if is_cached:
                for previous_alert in previous_rsi_alerts:
                    if previous_alert.ticker.symbol == ticker.symbol:
                        if (
                            (previous_alert.risk_level == 'Bearish' and ticker_price < previous_alert.currunt_price) or 
                            (previous_alert.risk_level == 'Bullish' and ticker_price > previous_alert.currunt_price)
                        ):
                            print("success")
                            result = Result.objects.get(strategy='RSI',time_frame=timespan)
                            result.success += 1
                            result.total += 1
                            result.result_value = (result.success / result.total)*100
                            result.save()
                        else:
                            print("filed")
                            result = Result.objects.get(strategy='RSI',time_frame=timespan)
                            result.total += 1
                            result.result_value = (result.success / result.total)*100
                            result.save()
                        previous_rsi_alerts.remove(previous_alert)
                        print(previous_rsi_alerts)
                        break
            # print(previous_rsi_alerts)
            if rsi_value > 70:
                risk_level = 'Bearish'
            if rsi_value < 30:
                risk_level = 'Bullish'
            if risk_level != None:
                alert = Alert.objects.create(ticker=ticker , strategy= 'RSI' ,time_frame=timespan ,risk_level=risk_level , result_value = rsi_value , currunt_price= 15.0)
                alert.save()  
                rsi_data.append(alert)
    if is_cached:
        cache.delete(f"RSI_{timespan}")
    if previous_rsi_alerts != [] and previous_rsi_alerts != None:
        previous_rsi_alerts = rsi_data.extend(previous_rsi_alerts) ## to add 2 lists together in one list
        cache.set(f"RSI_{timespan}", previous_rsi_alerts, timeout=86400*2)
        print("cache done")
    elif rsi_data != []:
        cache.set(f"RSI_{timespan}", rsi_data, timeout=86400*2)
        print("cache rsi data")
    print('**************************************')
    print(cache.get(f"RSI_{timespan}"))
    print('**************************************')
@api_view(['GET'])
def rsi_1day(request):
    rsi('1day')
    return Response({"j":"n"})

# @api_view(['GET'])
# def RedditScraper(request):
def RedditScraper():
    # execution of CHrome driver
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("disable-infobars")
    driver = webdriver.Chrome() 
    print("driver executed")

    # Getting tickers 
    TickerList = get_cached_queryset()
     
    RedditAccounts =["r/wallstreetbets", "r/shortsqueeze"]
    
    TickerCount = {ticker.symbol: 0 for ticker in TickerList}
    TickerCommentCount = {ticker: 0 for ticker in TickerList}

    for account in RedditAccounts:
        driver.get(f"https://www.reddit.com/" + account + "/new/")
        print(f"scraping {account}")
        previous_posts = []
        # presence of the account without scrolling
        try:
            WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//article[@class='w-full m-0']")))
        except Exception as e:
            return Response({"error": e})
        f = True
        # finding the posts with scrolling
        while True:
            posts = driver.find_elements(By.XPATH, "//article[@class='w-full m-0']")
            print(f"the length of posts = {len(posts)}")
            for post in posts:
                if f:
                    previous_posts.append(post)
                    f = False
                    continue
                if post not in previous_posts:
                    FlairClass = post.find_element(By.XPATH, ".//shreddit-post-flair").text
                    if "Meme" in FlairClass or "MEME" in FlairClass or "meme" in FlairClass:
                        print("meme")
                        continue
                    print(f"FlairClass: {FlairClass}")
                    TimePosted = post.find_element(By.TAG_NAME ,"time").text
                    hour = int(TimePosted.split()[0])
                    #check the time of post before entering it
                    if (hour < 23 or "min." in TimePosted) and "day" not in TimePosted:

                        article = post.find_element(By.XPATH, ".//shreddit-post/a")
                        # opening a new tab and switching to it
                        href = article.get_attribute("href")
                        driver.execute_script("window.open(arguments[0]);", href)
                        driver.switch_to.window(driver.window_handles[-1])
                        # collecting data from post
                        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                        text =  driver.find_element(By.XPATH, '//h1[@slot="title"]').text
                        try:
                            text2 = driver.find_element(By.XPATH, '//div[@class="text-neutral-content"]').text
                        except:
                            text2 = ""
                        text = text + " " + text2
                        for ticker in TickerList:
                            # Construct the regex pattern to match the ticker with symbols
                            ticker_pattern = r'[$#]?[\{\[]?' + re.escape(ticker.symbol) + r'[\}\]]?\b'
                            pattern = re.compile(ticker_pattern)
                            # If the ticker is found, increment its count in the dictionary
                            if pattern.search(text):
                                TickerCount[ticker.symbol] += 1        
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        previous_posts.append(post)
                        print("collected")
                    else:
                        break
            LatestPost = posts[-1]
            TimePosted = LatestPost.find_element(By.TAG_NAME ,"time").text
            hour = int(TimePosted.split()[0])
            if (hour < 6 or "min." in TimePosted) and "day" not in TimePosted:
                print("scrolling")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            else: 
                break

    return Response(TickerCount)


## scraping test endpoint ##
@api_view(['GET'])
def ScrapTest(request):
    twitter_scraper()
    return Response({"message":"screped successfully!"})

## test reduplication ##
@api_view(['GET'])
def reduplication(request):
    tickers = Ticker.objects.filter(symbol='NL')
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
                            test_query_set = Alert.objects.filter(ticker=ticker,strategy='Unusual Option Buys',time_frame='1day',result_value=volume,
                                                              risk_level= 'Call' ,investor_name=contract_id , amount_of_investment= avg_30_day_call_volume).order_by('-date','-time')[0]
                            if not test_query_set:
                                print("done1")
                                alert = Alert.objects.create(ticker=ticker 
                                    ,strategy='Unusual Option Buys' ,time_frame='1day' ,result_value=volume, 
                                    risk_level= 'Call' ,investor_name=contract_id , amount_of_investment= avg_30_day_call_volume)
                    else:
                        if float(volume) > float(avg_30_day_put_volume):
                            test_query_set = Alert.objects.filter(ticker=ticker,strategy='Unusual Option Buys',time_frame='1day',result_value=volume,
                                                              risk_level= 'Put' ,investor_name=contract_id , amount_of_investment= avg_30_day_call_volume).order_by('date','-time')[0]
                            if not test_query_set:
                                print("done2")
                                alert = Alert.objects.create(ticker=ticker 
                                    ,strategy='Unusual Option Buys' ,time_frame='1day' ,result_value=volume, 
                                    risk_level= 'Put' ,investor_name=contract_id , amount_of_investment= avg_30_day_put_volume)
                                alert.save()
            except BaseException:
                continue
        except BaseException :
            continue
    return Response({"message":"done"}) 

@api_view(['GET'])
def test_reddit(request):
    x = Reddit_API_Response(returned_dict={},our_symbol=our_symbols)
    print(x)
    return Response({"message":"hh"})

###########################################
def print_caching(*args,**kwargs):
    caching_rsi = cache.get("TodayAlerts_rsi_1day")
    caching_ema = cache.get("TodayAlerts_ema_1day")
    print("yes yes yes yes")
    print(f"caching rsi Before {caching_rsi}") 
    print(f"caching ema Before {caching_ema}") 
    print('rsi',len(caching_rsi))
    print('ema',len(caching_ema))
    if len(caching_rsi) > len(caching_ema):
        taller = caching_rsi
        smaller = caching_ema
    else:
        taller = caching_ema
        smaller = caching_rsi
    for key , value in taller.items():
        smaller[key].extend(value)
    print("after compination")
    print("smaller",smaller)
    caching_rsi.clear()
    caching_ema.clear()
    print(f"caching rsi After clear {caching_rsi}")
    print(f"caching ema After clear {caching_ema}")
    return "done"

## test earning ##
# @api_view(['GET'])
# def earn_scrap(request):
#     tasks = group(
#                 RSI_1day(),
#                 EMA_DAY(),)
#     workflow = chord(tasks)(print_caching())
#     return Response({"message":"sh"})


## endpoint to add tickers ##
# def add_tickers(request):
#     #######################################
#     # Path to your CSV file
#     input_file = 'output.csv'

#     # Open the input file for reading
#     with open(input_file, 'r', newline='') as csv_file:
#         reader = csv.reader(csv_file)

#         # Get the header (first row) to identify column names
#         header = next(reader)
#         print(header)
        
#         # Convert rows to columns (transpose the data)
#         columns = list(zip(*reader))
#         listy = []
#         # Loop through each column
#         for i, column in enumerate(columns):
#             if i == 4:
#                 for value in column:
#                     listy.append(value)
#                 print("length of list",len(listy))
#                 sorty = set(listy)
#                 sorty.remove('')
#                 print(sorty)
#                 print("len of set",len(sorty))

#         for ind in sorty:
#             Industry.objects.create(type= ind)
#     #######################################
#     return Response({"message":"tickers added successfully"})
## endpoint to add tickers ##
@api_view(['GET'])
def add_tickers(request):
    #######################################
    # Path to your CSV file
    input_file = 'output.csv'

    with open(input_file, 'r', newline='') as csv_file:
        reader = csv.reader(csv_file)
        
        # Skip the header
        next(reader)
        
        # Loop through each row, starting from the first data row (after header)
        for row_num, row in enumerate(reader, start=1):
            try:
                # Extract and print data from specific columns
                # print(row[4])  # Industry
                # print('symbol:', row[0])  # Symbol
                # print('name:', row[1])  # Name
                # print('market cap:', row[2])  # Market cap
                # print('industry:', row[4])  # Industry
                
                # Get or create the industry object
                industryy = Industry.objects.get(type=row[4].strip())
                print("found industry")
                print(industryy.type)
                
                # Create a Ticker object
                Ticker.objects.create(symbol=row[0], name=row[1], market_cap=float(row[2]), industry=industryy)
                print("done!")
            
            except Exception as e:
                # Handle any exceptions that occur
                print(e)
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                continue
    #######################################
    return Response({"message":"tickers added successfully"})

### test 13 f ###
list_of_CIK = ['0001067983']
@api_view(['GET'])
def get_13f(request):
    # print("getting 13F")
    api_key_fmd = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2' # 66ea9a91ce6fa7111ef41849
    day = str(dt.today().date())
    # print(day.date())
    # print(type(day.date()))
    strategy = '13F strategy'
    for cik in list_of_CIK:
        response = requests.get(f'https://financialmodelingprep.com/api/v4/institutional-ownership/portfolio-holdings?date=2024-06-30&cik={cik}&page=0&apikey={api_key_fmd}').json()
        # print('response: ',response)
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
                            alert = Alert.objects.create(investor_name = name , transaction_type = transaction , strategy=strategy,
                                                shares_quantity = abs(changeInSharesNumber) , ticker= ticker ,
                                                ticker_price=price , amount_of_investment=amount_of_investment)
                            alert.save()
                            WebSocketConsumer.send_new_alert(alert)
                        except:
                            continue
    return Response({"message":"13f successeded!"})

def Relative_Volume(ticker):
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

### common ##
@api_view(['GET'])
def tasks_1day(request):
    all_tickers = get_cached_queryset()
    print("got tickers")
    for ticker in all_tickers:
        print(ticker.symbol)
        ## initialize list of alerts that common on the same ticker ##
        list_alerts = []
        ## initialize list of applied functions for the time frame ##
        # applied_functions = [rsi(ticker=ticker, timespan='1day'),ema(ticker=ticker, timespan='1day')]
        applied_functions = [RS,EM]
        for function in applied_functions:
            alert = function(ticker=ticker, timespan='1day')
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
            alert = Alert.objects.create(ticker=ticker ,strategy='Common Alert', investor_name=message)
            alert.save()
            WebSocketConsumer.send_new_alert(alert)
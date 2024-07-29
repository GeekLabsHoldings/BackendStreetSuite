from Alerts.models import Tickers , Alerts_Details, Industry, Ticker , EMA_Alert , Rsi_Alert , Earning_Alert , Result ,Alert
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from .serializer import RSISerializer , AlertSerializer
from datetime import date , timedelta , datetime
from Alerts.OptionsScraper import main
from Payment.api.permissions import HasActiveSubscription
import requests
from Alerts.tasks import get_result 
from datetime import date as dt
from .paginations import AlertPAgination
from Alerts.ShortIntrestScraper import main as scrape_short_intrest
from django.core.cache import cache
from Alerts.tasks import rsi, Insider_Buyer, get_cached_queryset
from Alerts.OptionsScraper import main as earning_scraper

## view list alerts ###
class AlertListView(ListAPIView):
    # permission_classes = [HasActiveSubscription]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    pagination_class = AlertPAgination
    filterset_fields = ["ticker__industry", "risk_level", "strategy", "ticker__market_capital"]
    search_fields = ['ticker__symbol']
    queryset = Alert.objects.all().order_by('-time_posted')
    serializer_class = AlertSerializer

def short_interset():
    tickers = Ticker.objects.all()
    data = []
    ## looping in tickers ##
    for ticker in tickers:
        data.append(ticker)
        print(ticker.symbol)
    ## get all short interest value ##
    short_interset_values = scrape_short_intrest(data)
    ## looping in results ##
    for key , value in short_interset_values.items():
        print(key)
        print(value)
        ticker_data = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey=juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2').json()
        if ticker_data != []:
            industry_name = ticker_data[0]['industry']
            company_name = ticker_data[0]['companyName']
            market_cap = ticker_data[0]['mktCap']
            try:
                ticker2 = Ticker.objects.get(symbol=ticker)
            except :
                industry , created = Industry.objects.get_or_create(type=industry_name)
                ticker2 = Ticker.objects.create(symbol=ticker , name=company_name ,market_cap=market_cap , industry=industry)
        value_string = value.strip("%")
        float_value = float(value_string)
        Alert.objects.create(ticker=ticker2,strategy='Short Interest',result_value=float_value)

@api_view(['GET'])
def hh(request):
    tickers = Ticker.objects.all()
    print(len(tickers))
    tickers2 = tickers[100:]
    print(len(tickers2))
    for ticker in tickers2:
        ticker.delete()
    tickerss = Ticker.objects.all()
    print(len(tickerss))
    return Response({"data":"data"})

def get_result(ticker , strategy , time_frame  , model):
    # logger.info("geting result")
    # day_time = datetime.now()
    day = dt.today()
    print(ticker.symbol)
    print(strategy)
    print("ll")
    try:
        if time_frame == '1day':
            date_day = day - timedelta(days=1)
            print("kk")
            ticker_data = model.objects.get(ticker=ticker , strategy=strategy , strategy_time=time_frame)
            print('1day')
            print(ticker_data.strategy)
        else:
            print('oo')
            ticker_data = model.objects.filter(ticker=ticker, strategy=strategy, strategy_time=time_frame).latest('id')
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

## view for Relative Volume strategy ##
@api_view(['GET'])
def volume(request):
    tickers = Ticker.objects.all()
    for ticker in tickers:
        response = requests.get(f'https://financialmodelingprep.com/api/v3/quote/{ticker.symbol}?apikey=juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2').json()
        volume = response[0]['volume']
        avgVolume = response[0]['avgVolume']
        if volume > avgVolume:
            value2 = int(volume) -int(avgVolume)
            value = (int(value2)/int(avgVolume)) * 100
            print(value)
            print(avgVolume)
            print(value2)
            print("volume"+str(volume))
            Alert.objects.create(ticker=ticker ,strategy='Relative Volume' ,strategy_value=value ,risk_level= 'overbought avarege')
    return Response({"message":"hello"})


def avg():
    tickers = Ticker.objects.all()
    print(len(tickers))
    token = 'a4c1971d-fbd2-417e-a62d-9b990309a3ce'  # Replace with your actual token
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'  # Optional, depending on the API requirements
    }
    data = []
    for ticker in tickers:
        response = requests.get(
            f'https://api.unusualwhales.com/api/stock/{ticker.symbol}/options-volume',
            headers=headers
        ).json()
        
        try:
            ## to get avg of put and call ##
            avg_30_day_call_volume = response['data'][0]['avg_30_day_call_volume']
            # print(avg_30_day_call_volume ) 
            avg_30_day_put_volume = response['data'][0]['avg_30_day_put_volume']
            # print(avg_30_day_put_volume ) 
            contract_options = requests.get(f'https://api.unusualwhales.com/api/stock/{ticker.symbol}/option-contracts',headers=headers).json()['data']
            try:
                for contract in contract_options:
                    volume = contract['volume']
                    contract_id = contract['option_symbol']
                    # print(contract_id)
                    if contract_id[-9] == 'C':
                        if float(volume) > float(avg_30_day_call_volume):
                            print("call"+contract_id)
                            data.append(f'There is unusaual activity in the option contract {contract_id} C 17/2, the average volume is {volume}, and the current volume is {avg_30_day_call_volume}, which is call.')
                    else:
                        if float(volume) > float(avg_30_day_put_volume):
                            print("put"+contract_id)
                            data.append(f'There is unusaual activity in the option contract {contract_id} C 17/2, the average volume is {volume}, and the current volume is {avg_30_day_put_volume}, which is put.')
            except BaseException:
                # print(contract_id)
                continue
        except BaseException :
            # print(contract_id)
            continue
    return data

@api_view(['GET'])
def jojo(request):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    tickers = Ticker.objects.all()
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
                    print(ticker.symbol)
                else:
                    break
    return Response(response)


@api_view(['GET'])
def test(request):
    timespan = '1day'
    strategy = f'RSI strategy'
    strategy_time = timespan
    tickers = Ticker.objects.all()
    # data = []
    for ticker in tickers:
        print(f'{ticker.symbol}')
        risk_level = None
        result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='rsi')
        if result != []:
            rsi_value = result[0]['rsi']
            date = result[0]['date']
            status = None
            if rsi_value > 70:
                status = 'Overbought'
                risk_level = 'Bearish'
                print("berish")
            if rsi_value < 30:
                status = 'Underbought'
                risk_level = 'Bullish'
                print('bullish')
            # message = f"Using rsi Strategy, The Ticker {ticker} , this Stock is {status} and its risk_level {risk_level}, with rsi value = {rsi_value} in date {date} "
            if risk_level == None:
                Alert.objects.create(ticker=ticker , strategy= strategy ,strategy_time=strategy_time ,risk_level=risk_level , strategy_value = rsi_value )
    return Response({"message":"success"})

def getIndicator(ticker , timespan , type):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type={type}&period=14&apikey={api_key}')
    # print(data.json())
    return data.json()


## ema function ##
def ema(timespan):
    tickers = Ticker.objects.all()
    data = [{"mesage":"hi"}]
    for ticker in tickers:
        result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='ema')
        if result != []:
            risk_level = None
            ema_value = result[0]['ema']
            print(ema_value)
            currunt_price = result[0]['close']
            print(currunt_price)
            old_price = result[1]['close']
            print(old_price)
            if ema_value < currunt_price and ema_value > old_price:
                risk_level = 'Bullish'
            if ema_value > currunt_price and ema_value < old_price:
                risk_level = 'Bearish'
            if risk_level != None:
                get_result(ticker=ticker,strategy='EMA',time_frame=timespan,value=ema_value )   
    return data

## endpint for RSI 4 hours ##
@api_view(['GET'])
def RSI_4hour(request):
    data = rsi(timespan='4hour')
    return Response(data=data)

## endpint for RSI 1day ##
@api_view(['GET'])
def RSI_1day(request):
    data = rsi(timespan='1day')
    return Response(data=data)

## view for EMA  1day ##
@api_view(['GET'])
def EMA_DAY(request):
    data = ema(timespan='1day')
    return Response(data=data)

## view for EMA  4hour ##
@api_view(['GET'])
def EMA_4HOUR(request):
    data = ema(timespan='4hour')
    return Response(data=data)

## view for EMA  1hour ##
@api_view(['GET'])
def EMA_1HOUR(request):
    data = ema(timespan='1hour')
    return Response(data=data)
        

### view to get rsi for day ###
@api_view(['GET'])
def Alerts_In_Day(request):
    # response_messages = []
    timespan = '1day'
    
    tickers = Tickers.objects.all()
    data = []
    limit = 1
    for ticker in tickers:
        rsi_value_day = getIndicator(ticker=ticker.title, timespan='1day', type='rsi')[0]['rsi']
        rsi_value_4hours = getIndicator(ticker=ticker.title, timespan='4hour', type='rsi')[0]['rsi']
        ema_value_day = getIndicator(ticker=ticker.title, timespan='1day', type='ema')
        ema_value_4hpurs = getIndicator(ticker=ticker.title, timespan='4hour', type='ema')
        ema_value_1hour = getIndicator(ticker=ticker.title, timespan='1hour', type='ema')
        
        
        # rsi_data = getRSI(ticker=ticker.title, timespan=timespan, limit=limit)
        # limit = 1
        # if 'results' in rsi_data and 'values' in rsi_data['results']:
        #     RSI_value = rsi_data['results']['values'][0]['value']
        #     risk_level= 'Overbought' if RSI_value > 70 else 'Underbought' if RSI_value < 30 else 'none'
        #     if risk_level != 'none':
        #         data.append({
        #             'ticker': ticker.title,
        #             'RSI': RSI_value,
        #             'risk_level': risk_level,
        #             'message': f"Using RSI Strategy, {ticker} Stock is {risk_level}, Store Value as {'Bearish' if RSI_value > 70 else 'Bullish'}"
        #         })
        
        # risk_level = None 
                ##### ema ######
        # ema_data = getEMA(ticker=ticker.title, timespan=timespan, limit=limit)
        # if 'results' in ema_data and 'values' in ema_data['results']:
            
        #     EMA_value = ema_data['results']['values'][0]['value']
            
        #     current_price = ema_data["results"]["underlying"]["aggregates"][0]["c"]
        #     old_price = ema_data["results"]["underlying"]["aggregates"][1]["c"]
            
            
        #     if EMA_value < current_price and EMA_value > old_price:
        #         risk_level = 'Bullish'
        #     if EMA_value > current_price and EMA_value < old_price:
        #         risk_level = 'Bearish'

        #     if risk_level != None:
        #         data.append({
        #             'ticker': ticker.title,
        #             'EMA': EMA_value,
        #             'risk_level': risk_level,
        #             'message': f"Using EMA Strategy, The Ticker {ticker} with Price {current_price}, this Stock is {risk_level}, with EMA value = {EMA_value}"
        #         })
        #     else:
        #         data.append({
        #             'ticker': ticker.title,
        #             'EMA': EMA_value,
        #             'risk_level': risk_level,
        #             'message': f"price is {current_price}  and old price {old_price} and EMA {EMA_value}"
        #         })
    

    serializer = RSISerializer(data=data, many=True)
    serializer.is_valid()  # Validate the serializer data
    return Response(serializer.data)

## View for 13f ##
list_of_CIK = ['0001067983']
@api_view(['GET'])
def get_13f(request):
    api_key_fmd = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    day = date.today()
    data = {}
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
		"symbol": "TSLA",
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
		"changeInSharesNumber": -20000,
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
        for slice in response:
            changeInSharesNumber = slice['changeInSharesNumber']
            name = slice['investorName']
            symbol = slice['symbol']
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
                # return Response({"message":f'the amount of shares of {symbol}({price}$) = {changeInSharesNumber} and the total price of it is {amount_of_investment}'})
                data[symbol] = f'investor ({name}) invests the amount of shares of {symbol}({price}$) = {changeInSharesNumber} and the total price of it is {amount_of_investment}'
                # print(data)
            # else:
                # return Response({})
                # print('no')
    return Response(data)


###########################################
# def rr(models):
#     f = models.objects.get(symbol='TSLA')
#     g = f.name
#     print(f.symbol+f.name)

# @api_view(['GET'])
# def vevo(request):
#     rr(Ticker)
#     return Response({"message":"hh"})

## percntage success of strategy method ##
def percentage(ticker_symbol , time_period , strategy , risk_level , value , model_name):
    date_now = datetime.today()
    print(date_now)
    ticker = Ticker.objects.get(symbol=ticker_symbol)
    ticker_object = model_name.object.filter(ticker=ticker , strategy=strategy , strategy_time=time_period)

# percentage()
## test for get percentage of strategy success ##
@api_view(['GET'])
def strategy_success(request):
    ...

## Major Supports/Resistance ##
@api_view(['GET'])
def major(request):


    return Response({'message':'done'})

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
        list_ticker= []
        data= []
        for slice in response.json()[:80]:
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
                            list_ticker.append(ticker)
                            data.append({'ticker':ticker , 'strategy':'Earnings' ,'Estimated_Revenue':float(Estimated_Revenue), 'time':time , 'Estimated_EPS':float(Estimated_EPS)})
                    except:
                        continue
    print(len(list_ticker))
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

'https://financialmodelingprep.com/api/v3/otc/real-time-price/[ticker]?apikey=juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'

def short_interset():
    tickers = Ticker.objects.all()
    data = []
    ## looping in tickers ##
    for ticker in tickers[40:100]:
        print(ticker.symbol)
        data.append(ticker.symbol)
    ## get all short interest value ##
    short_interset_values = scrape_short_intrest(data)
    ## looping in results ##
    for key , value in short_interset_values.items():
        # ticker_data = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey=juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2').json()
        # if ticker_data != []:
        #     industry_name = ticker_data[0]['industry']
        #     company_name = ticker_data[0]['companyName']
        #     market_cap = ticker_data[0]['mktCap']
            # try:
        print(key)
        print(type(key))
        ticker2 = Ticker.objects.get(symbol=key)
            # except :
                # industry , created = Industry.objects.get_or_create(type=industry_name)
                # ticker2 = Ticker.objects.create(symbol=ticker , name=company_name ,market_cap=market_cap , industry=industry)
        value_string = value.strip("%")
        float_value = float(value_string)
        Alert.objects.create(ticker=ticker2,strategy='Short Interest',result_value=float_value)


@api_view(['GET'])
def uu(request):
    short_interset()
    return Response({"jj":"hh"})
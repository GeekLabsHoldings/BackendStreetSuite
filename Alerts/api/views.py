from Alerts.models import Tickers , Alerts_Details, Industry, Ticker, Alert , EMA_Alert , Rsi_Alert , Earning_Alert 
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from .serializer import RSISerializer, AlertSerializer
from datetime import date , timedelta , datetime
from Alerts.OptionsScraper import main
from Payment.api.permissions import HasActiveSubscription
import requests
from Alerts.tasks import get_result 
from datetime import date as dt

### view list alerts ###
class AlertListView(ListAPIView):
    permission_classes = [HasActiveSubscription]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["ticker__industry", "risk_level", "strategy", "ticker__market_capital"]
    search_fields = ['ticker__symbol']
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer


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
 

@api_view(['GET'])
def Earnings(request):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    ## today date ##
    today = date.today()
    thatday = today + timedelta(days=18) ## date after period time ##
    ## response of the api ##
    response = requests.get(f'https://financialmodelingprep.com/api/v3/earning_calendar?from={thatday}&to={thatday}&apikey={api_key}')
    # print(response.json())
    if response.json() != []:
        num2 = 0
        list_ticker= []
        data= []
        returned_data = []
        for slice in response.json():
            Estimated_EPS = slice['epsEstimated']
            testy = '.' in slice['symbol']
            if not testy:
                if Estimated_EPS != None :
                    # num.append(slice)
                    num2 += 1
                    ticker = slice['symbol']
                    time = slice['time']
                    Estimated_Revenue = slice['revenueEstimated']
                    list_ticker.append(ticker)
                    data.append({'ticker':ticker , 'strategy':'Earnings' ,'message':f'{ticker} after 15 days its , Estimated Revenue={Estimated_Revenue}, time={time} , '})
                    returned_data.append(slice)
                    # c = {"gg":"csd","ksdmk":"djs"}
                    # for i in c.items():
                    #     print(i[0])
                    #     print(i[1])
    ## get all Expected Moves  ##
    # result = main(list_ticker)
    # print(len(returned_data))
    # for x in result.items():
    #     for y in data:
    #         if x[0] == y['ticker']:
    #             y['Expected_Moves'] = x[1]
    #             y['message'] += f'Expected Moves={x[1]}'
    print(num2)
    return Response(data)

def common_alert():
    day = dt.today()
    data = []
    ## get rsi and ema alerts ##
    rsi_bearish = Rsi_Alert.objects.filter(risk_level='Bearish' , date=day)
    rsi_bullish = Rsi_Alert.objects.filter(risk_level='Bullish' , date=day)
    ema_bearish = EMA_Alert.objects.filter(risk_level='Bearish' , date=day)
    ema_bullish = EMA_Alert.objects.filter(risk_level='Bullish' , date=day)
    for alertx in rsi_bearish:
        for alerty in ema_bearish:
            if alertx.ticker == alerty.ticker:
                if alertx.ticker.symbol not in data:
                    data.append(alertx.ticker.symbol)

                    Rsi_Alert.objects.create(ticker=alertx.ticker , strategy= 'RSI & EMA', risk_level='Bearish')
    for alertx in rsi_bullish:
        for alerty in ema_bullish:
            if alertx.ticker == alerty.ticker:
                if alertx.ticker.symbol not in data:
                    data.append(alertx.ticker.symbol)
                    Rsi_Alert.objects.create(ticker=alertx.ticker , strategy= 'RSI & EMA', risk_level='Bullish')

### function for Earning strategy ###
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
                        print(ticker2.symbol)
                    finally:
                        time = slice['time']
                        Estimated_Revenue = slice['revenueEstimated']
                        list_ticker.append(ticker)
                        data.append({'ticker':ticker , 'strategy':'Earnings' ,'Estimated_Revenue':Estimated_Revenue, 'time':time , 'Estimated_EPS':Estimated_EPS ,})
                        # Alert.objects.create(ticker=ticker2 , strategy= 'Earning' ,strategy_time= duration ,risk_level=risk_level , strategy_value = rsi_value )

    ## get all Expected Moves by Scraping ##
    print(len(data))
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
                # print('yes')
@api_view(['GET'])
def jojo(request):
    Earnings(25)
    return Response({"message":"hh"})

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

def rsi(timespan):
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
            message = f"Using rsi Strategy, The Ticker {ticker} , this Stock is {status} and its risk_level {risk_level}, with rsi value = {rsi_value} in date {date} "
            if risk_level != None:
                # get_result(ticker=ticker,strategy='RSI',time_frame=timespan,value=rsi_value ,model=Rsi_Alert)
                Rsi_Alert.objects.create(ticker=ticker , strategy= 'RSI' ,strategy_time=timespan ,risk_level=risk_level , rsi_value = rsi_value )
                Alert.objects.create(ticker=ticker , strategy= 'RSI' ,strategy_time=timespan ,risk_level=risk_level , strategy_value = rsi_value )
                Alerts_Details.objects.create(ticker=ticker.symbol , strategy=f'RSI per {timespan}' , value=rsi_value , risk_level = risk_level,message=message)
            # return data

## ema function ##
def ema(timespan):
    tickers = Ticker.objects.all()
    data = [{"mesage":"hi"}]
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
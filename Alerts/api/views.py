from Alerts.models import Tickers , Alerts_Details
import requests
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from .serializer import RSISerializer, AlertSerializer
import json
from datetime import date , timedelta
from Alerts.tasks import EMA_4HOUR as gg
from Alerts.OptionsScraper import main

### view list alerts ###
class AlertListView(ListAPIView):
    today = date.today()
    queryset = Alerts_Details.objects.filter(date=today).order_by("-time")
    serializer_class = AlertSerializer


### view for Earnings strategy ###
@api_view(['GET'])
def Earnings(request):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    ## today date ##
    today = date.today()
    print(today)
    thatday = today + timedelta(days=15) ## date after period time ##
    print(thatday)
    ## response of the api ##
    response = requests.get(f'https://financialmodelingprep.com/api/v3/earning_calendar?from={thatday}&to={thatday}&apikey=juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2')
    # print(response.json())
    if response.json() != []:
        num2 = 0
        list_ticker= []
        data= []
        returned_data = []
        for slice in response.json():
            Estimated_EPS = slice['epsEstimated']
            if Estimated_EPS != None :
                # num.append(slice)
                num2 += 1
                ticker = slice['symbol']
                time = slice['time']
                Estimated_Revenue = slice['revenueEstimated']
                list_ticker.append(ticker)
                data.append({'ticker':ticker , 'strategy':'Earnings' ,'message':f'{ticker} after 15 days its , Estimated Revenue={Estimated_Revenue}, time={time} , '})
    ## get all Expected Moves  ##
    result = main(list_ticker)
    for x in result.items():
        for y in data:
            if x[0] == y['ticker']:
                y['Expected_Moves'] = x[1]
                y['message'] += f'Expected Moves={x[1]}'
        # print(len(num))
    return Response(data=data)

@api_view(['GET'])
def test(request):
    gg()
    return Response({"message":"success"})

def getIndicator(ticker , timespan , type):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type={type}&period=14&apikey={api_key}')
    print(data.json())
    return data.json()

## rsi function ##
def rsi(timespan):
    tickers = Tickers.objects.all()
    data = []
    for ticker in tickers:
        risk_level = None
        result = getIndicator(ticker=ticker.title , timespan=timespan , type='rsi')
        rsi_value = result[0]['rsi']
        print(ticker.title+str(rsi_value))
        date = result[0]['date']
        if rsi_value > 70:
            risk_level = 'Overbought'
        if rsi_value < 30:
            risk_level = 'Underbought'
        if risk_level != None:
            data.append({
                        'ticker': ticker.title,
                        'rsi': rsi_value,
                        'risk_level': risk_level,
                        'message': f"Using rsi Strategy, The Ticker {ticker} , this Stock is {risk_level}, with rsi value = {rsi_value} in date {date} "
                    })
            return data

## ema function ##
def ema(timespan):
    tickers = Tickers.objects.all()
    data = []
    for ticker in tickers:
        result = getIndicator(ticker=ticker.title , timespan=timespan , type='ema')
        risk_level = None
        ema_value = result[0]['ema']
        print(ema_value)
        currunt_price = result[0]['close']
        old_price = result[1]['close']
        if ema_value < currunt_price and ema_value > old_price:
            risk_level = 'Bullish'
        if ema_value > currunt_price and ema_value < old_price:
            risk_level = 'Bearish'
        if risk_level != None:
            data.append({
                        'ticker': ticker.title,
                        'EMA': ema_value,
                        'risk_level': risk_level,
                        'message': f"Using EMA Strategy, The Ticker {ticker} with Price {currunt_price}, and old price {old_price} this Stock is {risk_level}, with EMA value = {ema_value}"
                    })
        # else:
            # data.append({
            #     'ticker': ticker.title,
            #     'EMA': ema_value,
            #     'risk_level': risk_level,
            #     'message': f"price is {currunt_price}  and old price {old_price} and EMA {ema_value}"
            # })
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


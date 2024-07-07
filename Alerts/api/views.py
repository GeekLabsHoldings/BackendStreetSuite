from Alerts.models import Tickers
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import RSISerializer
import json

### method for request on the url ### 
def getRSI(ticker , timespan , limit):
    api_key = 'D6OHppxED0AddEE_9EUzkYpGT6zxoJ9A'
    data = requests.get(f'https://api.polygon.io/v1/indicators/rsi/{ticker}?timespan={timespan}&adjusted=true&window=14&series_type=close&order=desc&limit={limit}&apiKey={api_key}')
    return data.json()

def getEMA(ticker, timespan, limit):
    api_key = 'D6OHppxED0AddEE_9EUzkYpGT6zxoJ9A'
    data = requests.get(f'https://api.polygon.io/v1/indicators/ema/{ticker}?timespan={timespan}&adjusted=true&window=50&series_type=close&order=desc&limit={limit}&apiKey={api_key}')
    return data.json()

### view to get rsi for day ###
@api_view(['GET'])
def RSIoneDay(request):
    # response_messages = []
    timespan = 'day'
    limit = 1
    tickers = Tickers.objects.all()
    data = []
    
    for ticker in tickers:
        rsi_data = getRSI(ticker=ticker.title, timespan=timespan, limit=limit)
        
        if 'results' in rsi_data and 'values' in rsi_data['results']:
            RSI_value = rsi_data['results']['values'][0]['value']
            risk_level= 'Overbought' if RSI_value > 70 else 'Underbought' if RSI_value < 30 else 'none'
            if risk_level != 'none':
                data.append({
                    'ticker': ticker.title,
                    'RSI': RSI_value,
                    'risk_level': risk_level,
                    'message': f"Using RSI Strategy, {ticker} Stock is {risk_level}, Store Value as {'Bearish' if RSI_value > 70 else 'Bullish'}"
                })

        ema_data = getEMA(ticker=ticker.title, timespan=timespan, limit=limit)
        if 'results' in ema_data and 'values' in ema_data['results']:
            EMA_value = ema_data['results']['values'][0]['value']
            risk_level= 'Bullish' if EMA_value > 200 else 'Bearish' if EMA_value < 200 else 'none'
            if risk_level != 'none':
                data.append({
                    'ticker': ticker.title,
                    'EMA': EMA_value,
                    'risk_level': risk_level,
                    'message': f"Using EMA Strategy, {ticker} Stock is {risk_level}, EMA value is {EMA_value}"
                })


    serializer = RSISerializer(data=data, many=True)
    serializer.is_valid()  # Validate the serializer data
    return Response(serializer.data)

### view to get rsi for 4 hours ###
@api_view(['GET'])
def RSI4hours(request):
    # response_messages = []
    timespan = 'hour'
    limit = 4
    tickers = Tickers.objects.all()
    data = []
    
    for ticker in tickers:
        returned_data = getRSI(ticker=ticker.title, timespan=timespan, limit=limit)
        
        if 'results' in returned_data and 'values' in returned_data['results']:
            RSI_value = returned_data['results']['values'][0]['value']
            risk_level= 'Overbought' if RSI_value > 70 else 'Underbought' if RSI_value < 30 else 'none'
            if risk_level != 'none':
                data.append({
                    'ticker': ticker.title,
                    'RSI': RSI_value,
                    'risk_level': risk_level,
                    'message': f"{ticker} Stock is {risk_level} , Store Value as {'Bearish' if RSI_value > 70 else 'Bullish'}"
                })

    serializer = RSISerializer(data=data, many=True)
    serializer.is_valid()  # Validate the serializer data
    return Response(serializer.data)


    # response_messages = []
    # timespan= 'day'
    # limit = 1
    # tickers = Tickers.objects.all()
    # data = {}
    # test = {}
    # for ticker in tickers:
    #     risk_level = ''
    #     returned_data = getRSI(ticker=ticker.title , timespan=timespan , limit=limit)
    #     # if 'values' in returned_data:
    #     test[ticker.title] = returned_data
        
    #     RSI_value = test[str(ticker.title)]["results"]["values"][0]['value']
    #     data[ticker.title] = RSI_value
        
    #     if RSI_value > 70:
    #         risk_level = 'Overbought'
    #         message = f"{ticker} Stock is {risk_level}, Store Value as Bearish"
    #         response_messages.append(message)
    #     if RSI_value < 30:
    #         risk_level = 'Underbought'
    #         message = f"{ticker} Stock is {risk_level}, Store Value as Bullish"
    #         response_messages.append(message)
        
    # serialized_messages = [{"message": msg} for msg in response_messages]
    # return Response(serialized_messages)


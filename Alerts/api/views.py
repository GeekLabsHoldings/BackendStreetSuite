from Alerts.models import Tickers
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import RSISerializer
import json

def getIndicator(ticker , timespan , type):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type={type}&period=14&apikey={api_key}')
    return data.json()

### view to get rsi for day ###
@api_view(['GET'])
def Alerts_In_Day(request):
    # response_messages = []
    timespan = '1day'
    
    tickers = Tickers.objects.all()
    data = []
    limit = 1
    for ticker in tickers:
        rsi_data = getIndicator(ticker=ticker.title, timespan=timespan, type='rsi')[0]['rsi']
        data.append({
            'ticker' : ticker.title,
            'message': rsi_data
            })
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

### view to get rsi for 4 hours ###
# @api_view(['GET'])
# def RSI4hours(request):
#     # response_messages = []
#     timespan = 'hour'
#     limit = 4
#     tickers = Tickers.objects.all()
#     data = []
    
#     for ticker in tickers:
#         returned_data = getRSI(ticker=ticker.title, timespan=timespan, limit=limit)
        
#         if 'results' in returned_data and 'values' in returned_data['results']:
#             RSI_value = returned_data['results']['values'][0]['value']
#             risk_level= 'Overbought' if RSI_value > 70 else 'Underbought' if RSI_value < 30 else 'none'
#             if risk_level != 'none':
#                 data.append({
#                     'ticker': ticker.title,
#                     'RSI': RSI_value,
#                     'risk_level': risk_level,
#                     'message': f"{ticker} Stock is {risk_level} , Store Value as {'Bearish' if RSI_value > 70 else 'Bullish'}"
#                 })

#     serializer = RSISerializer(data=data, many=True)
#     serializer.is_valid()  # Validate the serializer data
#     return Response(serializer.data)


#     # response_messages = []
#     # timespan= 'day'
#     # limit = 1
#     # tickers = Tickers.objects.all()
#     # data = {}
#     # test = {}
#     # for ticker in tickers:
#     #     risk_level = ''
#     #     returned_data = getRSI(ticker=ticker.title , timespan=timespan , limit=limit)
#     #     # if 'values' in returned_data:
#     #     test[ticker.title] = returned_data
        
#     #     RSI_value = test[str(ticker.title)]["results"]["values"][0]['value']
#     #     data[ticker.title] = RSI_value
        
#     #     if RSI_value > 70:
#     #         risk_level = 'Overbought'
#     #         message = f"{ticker} Stock is {risk_level}, Store Value as Bearish"
#     #         response_messages.append(message)
#     #     if RSI_value < 30:
#     #         risk_level = 'Underbought'
#     #         message = f"{ticker} Stock is {risk_level}, Store Value as Bullish"
#     #         response_messages.append(message)
        
#     # serialized_messages = [{"message": msg} for msg in response_messages]
#     # return Response(serialized_messages)

# @api_view(['GET'])
# def Alerts_In_Hour():
#     timespan = 'hour'
#     limit = 1
#     tickers = Tickers.objects.all()
#     data = []
#     for ticker in tickers:
#         # rsi_data = getRSI(ticker=ticker.title, timespan=timespan, limit=limit)
#         # limit = 1
#         # if 'results' in rsi_data and 'values' in rsi_data['results']:
#         #     RSI_value = rsi_data['results']['values'][0]['value']
#         #     risk_level= 'Overbought' if RSI_value > 70 else 'Underbought' if RSI_value < 30 else 'none'
#         #     if risk_level != 'none':
#         #         data.append({
#         #             'ticker': ticker.title,
#         #             'RSI': RSI_value,
#         #             'risk_level': risk_level,
#         #             'message': f"Using RSI Strategy, {ticker} Stock is {risk_level}, Store Value as {'Bearish' if RSI_value > 70 else 'Bullish'}"
#         #         })
        
#         risk_level = None 
#         ema_data = getEMA(ticker=ticker.title, timespan=timespan, limit=limit)
#         if 'results' in ema_data and 'values' in ema_data['results']:
            
#             EMA_value = ema_data['results']['values'][0]['value']
            
#             current_price = ema_data["results"]["underlying"]["aggregates"][0]["c"]
#             old_price = ema_data["results"]["underlying"]["aggregates"][1]["c"]
            
            
#             if EMA_value < current_price and EMA_value > old_price:
#                 risk_level = 'Bullish'
#             if EMA_value > current_price and EMA_value < old_price:
#                 risk_level = 'Bearish'

#             if risk_level != None:
#                 data.append({
#                     'ticker': ticker.title,
#                     'EMA': EMA_value,
#                     'risk_level': risk_level,
#                     'message': f"Using EMA Strategy, The Ticker {ticker} with Price {current_price}, this Stock is {risk_level}, with EMA value = {EMA_value}"
#                 })
#             else:
#                 data.append({
#                     'ticker': ticker.title,
#                     'EMA': EMA_value,
#                     'risk_level': risk_level,
#                     'message': f"price is {current_price}  and old price {old_price} and EMA {EMA_value}"
#                 })

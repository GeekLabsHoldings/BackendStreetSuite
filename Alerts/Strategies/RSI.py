from Alerts.models import Ticker , Result ,  Alert
from django.core.cache import cache
from ..consumers import WebSocketConsumer
import requests

def get_cached_queryset():
    queryset = cache.get("tickerlist")
    if not queryset:
        queryset = Ticker.objects.all()
        cache.set("tickerlist", queryset, timeout=86400)
    return queryset

def GetRSIStrategy(timespan):
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    tickers = get_cached_queryset()
    result_strategy = Result.objects.get(strategy='RSI',time_frame=timespan)
    result_success = 0
    result_total = 0
    i = 0
    for ticker in tickers[:100]:
        i += 1
        print(f"RSI {timespan},{i}")
        risk_level = None
        ticker_price = None
        data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker}?type=rsi&period=14&apikey={api_key}')
        result = data.json()
        if result != []:
            print(ticker.symbol)
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
                    alert = Alert.objects.create(ticker=ticker , strategy= 'RSI' ,time_frame=timespan ,risk_level=risk_level , result_value = rsi_value , current_price = ticker_price)
                    alert.save()  
                    WebSocketConsumer.send_new_alert(alert)

                except:
                    continue
    ## calculate the total result of strategy ##
    result_strategy.success += result_success
    result_strategy.total += result_total
    result_strategy.save()
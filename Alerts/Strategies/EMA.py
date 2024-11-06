from Alerts.models import Result,  Alert
from ..consumers import WebSocketConsumer
import requests
from django.conf import settings


def GetEMAStrategy(ticker,timespan):
    api_key = settings.FMP_API_KEY
    # print(f"ema {ticker.symbol}")
    ## initialize results parameters ##
    result_strategy = Result.objects.get(strategy='EMA',time_frame=timespan)
    result_success = 0
    result_total = 0
    i = 0
    i += 1
    data = requests.get(f'https://financialmodelingprep.com/api/v3/technical_indicator/{timespan}/{ticker.symbol}?type=ema&period=14&apikey={api_key}')
    result = data.json()
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
                alert = Alert.objects.create(ticker=ticker , strategy= 'EMA' ,time_frame=timespan ,risk_level=risk_level , result_value = ema_value, current_price=current_price)
                alert.save()
                # Update the cache with the modified queryset
                WebSocketConsumer.send_new_alert(alert)
                return alert
            except:
                return None
    result_strategy.success += result_success
    result_strategy.total += result_total
    result_strategy.save()

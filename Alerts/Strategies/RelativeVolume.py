from Alerts.models import Result,  Alert
from ..consumers import WebSocketConsumer
from django.core.cache import cache
import requests
from django.conf import settings
from Alerts.models import Ticker

def get_cached_queryset():
    queryset = cache.get("tickerlist")
    if not queryset:
        queryset = Ticker.objects.all()
        cache.set("tickerlist", queryset, timeout=86400)
    return queryset

def GetRelativeVolume():
    tickers = get_cached_queryset()
    for ticker in tickers:
        # print(ticker.symbol)
        is_cached = True
        previous_volume_alerts = cache.get('relative_volume_alerts')
        volume_alerts = []
        if not previous_volume_alerts:
            is_cached = False
        api_key = settings.FMP_API_KEY
        ## initialize the parameter to calculate result ##
        result_success = 0
        result_total = 0
        
        response = requests.get(f'https://financialmodelingprep.com/api/v3/quote/{ticker.symbol}?apikey={api_key}').json()
        try:
            volume = response[0]['volume']
            # print(f"volume :{volume}")
            avgVolume = response[0]['avgVolume']
            # print(f"avgVolume :{avgVolume}")
            current_price = response[0]['price']
            # print(f"current_price :{current_price}")
        except Exception as e:
            print({"Error": e})
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
                # print(f"value ratio {value}")
                try:
                    alert = Alert.objects.create(ticker=ticker ,strategy='Relative Volume' ,result_value=value ,risk_level= 'overbought average', current_price=current_price)
                    alert.save()
                    # print("new alert created")
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
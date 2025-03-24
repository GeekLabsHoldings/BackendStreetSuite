from Alerts.models import Alert
import requests, time
from ..consumers import WebSocketConsumer
from django.conf import settings


def GetUnusualOptionBuys(ticker, future): 
    token = settings.UNUSUALWHALES_TOKEN 
    obj = None

    ## for Authentication on request ##
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'  
    }
    # response = requests.get(
    #     f'https://api.unusualwhales.com/api/stock/{ticker.symbol}/options-volume', headers=headers).json() 
    try:
        ## to get avg of call transaction ##
        # avg_30_day_call_volume = response['data'][0]['avg_30_day_call_volume']
        ## average number of put transaction ##
        # avg_30_day_put_volume = response['data'][0]['avg_30_day_put_volume']
        ### get all contracts for each ticker ###    
        contract_options = requests.get(f'https://api.unusualwhales.com/api/stock/{ticker.symbol}/option-contracts?expiry={future}',headers=headers).json()['data']
        if contract_options != [] :
            for contract in contract_options:
                premium = contract['total_premium']
                obj = {
                    'result_value': premium,
                }
                #     if float(volume) > float(avg_30_day_call_volume):
                #         # alert = Alert.objects.create(ticker=ticker 
                #         #     ,strategy='Unusual Option Buys' ,time_frame='1day' ,result_value=volume, 
                #         #     risk_level= 'Call' ,investor_name=contract_id , amount_of_investment= avg_30_day_call_volume)
                #         # alert.save()
                #         # WebSocketConsumer.send_new_alert(alert)
                #         obj = {
                #             'strategy': 'Unusual Option',
                #             'result_value': volume,
                #             'risk_level': 'Call',

                #         }
            #else:
                # if float(volume) > float(avg_30_day_put_volume):
                #     # alert = Alert.objects.create(ticker=ticker 
                #         # ,strategy='Unusual Option Buys' ,time_frame='1day' ,result_value=volume, 
                #         # risk_level= 'Put' ,investor_name=contract_id , amount_of_investment= avg_30_day_put_volume)
                #     # alert.save()
                #     # WebSocketConsumer.send_new_alert(alert)
                #     obj = {
                        
                #         'result_value': volume,
                #         'risk_level': 'Put',

                #     }

        if obj != None:
            return obj
        else: 
            return None
    except Exception as e:
        return None
        
    
    
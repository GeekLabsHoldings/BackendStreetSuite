from celery import shared_task
from .models import Tickers
from QuizApp.models import UserEmail
# app = Celery('Streetsuite', broker='redis://localhost:6379')
import requests
from Alerts.models import PercentageOfRSI



def getEMA(ticker, timespan, limit):
    api_key = 'D6OHppxED0AddEE_9EUzkYpGT6zxoJ9A'
    data = requests.get(f'https://api.polygon.io/v1/indicators/ema/{ticker}?timespan={timespan}&adjusted=true&window=200&series_type=close&expand_underlying=true&order=desc&limit={limit}&apiKey={api_key}')
    return data.json()

@shared_task
def Working():
    user_email = UserEmail.objects.get(id=6)
    user_email.result = user_email.result + 1.1
    user_email.save()
    # timespan = 'day'
    # tickers = Tickers.objects.all()
    
    # for ticker in tickers:
    #     print(ticker.title)
    #     limit = 1
    #     ema_data = getEMA(ticker=ticker.title, timespan=timespan, limit=limit)
    #     if 'results' in ema_data and 'values' in ema_data['results']:
    #         current_price = ema_data["results"]["underlying"]["aggregates"][0]["c"]
    #         perday = PercentageOfRSI(per_day=current_price)
    #         perday.save()
    print("Current Work")
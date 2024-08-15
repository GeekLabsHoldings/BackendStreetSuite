from Alerts.models import Alert , Result
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import ListAPIView
from .serializer import AlertSerializer
from .paginations import AlertPAgination
from .filters import AlertFilters
from rest_framework.decorators import api_view
from Alerts.ShortIntrestScraper import short_interest_scraper
from Alerts.models import Ticker
from rest_framework.response import Response
from Alerts.OptionsScraper import earning_scraping
from datetime import timedelta , date
import requests
from Alerts.tasks import MajorSupport , getIndicator
from datetime import datetime as dt
from django.core.cache import cache

## view list alerts ###
class AlertListView(ListAPIView):
    # permission_classes = [HasActiveSubscription]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    pagination_class = AlertPAgination
    filterset_class = AlertFilters
    search_fields = ['ticker__symbol']
    queryset = Alert.objects.all().order_by('-time_posted')
    serializer_class = AlertSerializer

@api_view(['GET'])
def MajorSupportTEST(request):
    MajorSupport('1hour')
    return Response({"message":"done"})

def get_cached_queryset():
    queryset = cache.get("tickerlist")
    if not queryset:
        # print("gotttt")
        queryset = Ticker.objects.all()
        cache.set("tickerlist", queryset, timeout=86400)
    return queryset

@api_view(['GET'])
def test(request):
    tickers = Ticker.objects.all()
    for ticker in tickers[:60]:
        print(ticker.symbol)
        results = short_interest_scraper(ticker.symbol)
        print(results)
        if results >= 30:
            print('yes')
            Alert.objects.create(ticker=ticker,strategy='Short Interest',result_value=results)
    return Response({"gg":"hh"})


@api_view(['GET'])
def Earnings(request):
    # value = redis_client.get('tickers')
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    ## token for request on currunt IV ##
    token = 'a4c1971d-fbd2-417e-a62d-9b990309a3ce'  
    ## today date ##
    today = dt.today()
    thatday = today + timedelta(days=15) ## date after period time ##
    print(thatday)
    ## for Authentication on request for currunt IV ##
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'  # Optional, depending on the API requirements
    }
    ## response of the api ##
    response = requests.get(f'https://financialmodelingprep.com/api/v3/earning_calendar?from={thatday}&to={thatday}&apikey={api_key}')
    if response.json() != []:
        print(len(response.json()))
        for slice in response.json()[:1000]:
            Estimated_EPS = slice['epsEstimated']
            dotted_ticker = '.' in slice['symbol']
            if not dotted_ticker and Estimated_EPS != None :
                ticker = slice['symbol']
                print(ticker)
                try:
                    ticker2 = Ticker.objects.get(symbol=ticker)
                    time = slice['time']
                    if time != '--':
                        print('time'+time)
                        Estimated_Revenue = slice['revenueEstimated']
                        print('Estimated_Revenue')
                        print(Estimated_Revenue) 
                        # if Estimated_Revenue != None:
                        Expected_Moves = earning_scraping(ticker) 
                        current_IV = requests.get(f'https://api.unusualwhales.com/api/stock/{ticker}/option-contracts',headers=headers).json()['data'][0]['implied_volatility']
                        print('current_IV')
                        print(current_IV)
                        Alert.objects.create(ticker=ticker2 ,strategy= 'Earning', 
                                    time_frame = '15' , Estimated_Revenue = Estimated_Revenue, current_IV= current_IV ,
                                    Estimated_EPS = Estimated_EPS , Expected_Moves=Expected_Moves , earning_time=time)
                except:
                        continue

    return Response({"gg":"hh"})

@api_view(['GET'])
def short_interset(request):
    ticker = Ticker.objects.get(symbol='INVA')
    ## looping in tickers ##
    # for ticker in tickers[:10]:
    short_interset_value = short_interest_scraper(ticker.symbol) #get short interest value 
    if short_interset_value >=30: 
        print(short_interset_value)
        print(type(short_interset_value))
        Alert.objects.create(ticker=ticker,strategy='Short Interest',result_value=short_interset_value)
    return Response({"gg":"hh"})


## rsi function ##
def rsi(timespan):
    tickers = get_cached_queryset()
    is_cached = True
    previous_rsi_alerts = cache.get(f"RSI_{timespan}")
    print(previous_rsi_alerts)
    if not previous_rsi_alerts:
        is_cached = False
    rsi_data = []
    for ticker in tickers:
        risk_level = None
        ticker_price = None
        result = getIndicator(ticker=ticker.symbol , timespan=timespan , type='rsi')
        if result != []:
            try:
                rsi_value = result[0]['rsi']
                ticker_price = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{ticker.symbol}?apikey=juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2').json()[0]['price']
            except BaseException:
                continue
             ## to calculate results of strategy successful accourding to current price ##
            if is_cached:
                for previous_alert in previous_rsi_alerts:
                    if previous_alert.ticker.symbol == ticker.symbol:
                        if (
                            (previous_alert.risk_level == 'Bearish' and ticker_price < previous_alert.currunt_price) or 
                            (previous_alert.risk_level == 'Bullish' and ticker_price > previous_alert.currunt_price)
                        ):
                            print("success")
                            result = Result.objects.get(strategy='RSI',time_frame=timespan)
                            result.success += 1
                            result.total += 1
                            result.result_value = (result.success / result.total)*100
                            result.save()
                        else:
                            print("filed")
                            result = Result.objects.get(strategy='RSI',time_frame=timespan)
                            result.total += 1
                            result.result_value = (result.success / result.total)*100
                            result.save()
                        previous_rsi_alerts.remove(previous_alert)
                        print(previous_rsi_alerts)
                        break
            # print(previous_rsi_alerts)
            if rsi_value > 70:
                risk_level = 'Bearish'
            if rsi_value < 30:
                risk_level = 'Bullish'
            if risk_level != None:
                alert = Alert.objects.create(ticker=ticker , strategy= 'RSI' ,time_frame=timespan ,risk_level=risk_level , result_value = rsi_value , currunt_price= 15.0)
                alert.save()  
                rsi_data.append(alert)
                # print(rsi_data)
                # print('****************************')
                # print(previous_rsi_alerts)
                # if previous_rsi_alerts != None:
                #     previous_rsi_alerts = rsi_data.extend(previous_rsi_alerts) ## to add 2 lists together in one list
                # else:
                #     previous_rsi_alerts = rsi_data
    # print(rsi_data)

    if is_cached:
        cache.delete(f"RSI_{timespan}")
    if previous_rsi_alerts != [] and previous_rsi_alerts != None:
        previous_rsi_alerts = rsi_data.extend(previous_rsi_alerts) ## to add 2 lists together in one list
        cache.set(f"RSI_{timespan}", previous_rsi_alerts, timeout=86400*2)
        print("cache done")
    elif rsi_data != []:
        cache.set(f"RSI_{timespan}", rsi_data, timeout=86400*2)
        print("cache rsi data")
    print('**************************************')
    print(cache.get(f"RSI_{timespan}"))
    print('**************************************')
@api_view(['GET'])
def rsi_1day(request):
    rsi('1day')
    return Response({"j":"n"})

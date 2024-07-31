from Alerts.models import Alert
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
def earn(request):
    # value = redis_client.get('tickers')
    api_key = 'juwfn1N0Ka0y8ZPJS4RLfMCLsm2d4IR2'
    ## today date ##
    today = date.today()
    thatday = today + timedelta(days=27) ## date after period time ##
    print(thatday)
    ## response of the api ##
    response = requests.get(f'https://financialmodelingprep.com/api/v3/earning_calendar?from={thatday}&to={thatday}&apikey={api_key}')
    if response.json() != []:
        print(len(response.json()))
        for slice in response.json():
            Estimated_EPS = slice['epsEstimated']
            dotted_ticker = '.' in slice['symbol']
            if not dotted_ticker:
                if Estimated_EPS != None :
                    ticker = slice['symbol']
                    # print(ticker)
                    try:
                        ticker2 = Ticker.objects.first()
                        print(ticker2.symbol)
                        time = slice['time']
                        Estimated_Revenue = slice['revenueEstimated']
                        if Estimated_Revenue != None:

                            Expected_Moves = earning_scraping(ticker) 
                            if Expected_Moves.startswith('+'):
                                Alert.objects.create(ticker=ticker2 ,strategy= 'Earning', 
                                            time_frame = '15' , Estimated_Revenue = Estimated_Revenue, 
                                            Estimated_EPS = Estimated_EPS , Expected_Moves=Expected_Moves , earning_time=time)
                    except:
                        print("unkown ticker")

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



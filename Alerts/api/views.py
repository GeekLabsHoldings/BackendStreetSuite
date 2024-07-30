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
    tickers = Ticker.objects.all()
    for ticker in tickers[:10]:
        earning_scraping(ticker.symbol)

    return Response({"gg":"hh"})

@api_view(['GET'])
def short_interset(request):
    tickers = Ticker.objects.all()
    ## looping in tickers ##
    for ticker in tickers[:10]:
        short_interset_value = short_interest_scraper(ticker.symbol) #get short interest value 
        if short_interset_value >=30: 
            Alert.objects.create(ticker=ticker,strategy='Short Interest',result_value=short_interset_value)
    return Response({"gg":"hh"})



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
    for ticker in tickers[:10]:
        print(ticker.symbol)
        results = short_interest_scraper(ticker.symbol)
        print(results)
    return Response({"gg":"hh"})



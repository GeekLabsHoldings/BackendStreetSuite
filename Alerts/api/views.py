from Alerts.models import Alert , Ticker
from UserApp.models import Profile
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters , status
from rest_framework.generics import ListAPIView
from .serializer import AlertSerializer, TickerSerializer
from .paginations import AlertPAgination
from .filters import AlertFilters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from Payment.api.permissions import HasActiveSubscription
from ..Strategies.RSI import GetRSIStrategy
#########################
from datetime import date

## view list alerts ###
class AlertListView(ListAPIView):
    # permission_classes = [HasActiveSubscription]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    pagination_class = AlertPAgination
    filterset_class = AlertFilters
    search_fields = ['ticker__symbol']
    queryset = Alert.objects.filter(date__gte=date(2025, 3, 18)).order_by('-date', '-time')

    serializer_class = AlertSerializer

## view list alerts followed by user ###
class FollowedAlertListView(ListAPIView):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    pagination_class = AlertPAgination
    filterset_class = AlertFilters
    search_fields = ['ticker__symbol']
    serializer_class = AlertSerializer

    def get_queryset(self):
        # Get the user's profile
        profile = Profile.objects.get(user=self.request.user)
        followed_tickers = profile.followed_tickers
        # Filter alerts based on the followed_tickers list
        return Alert.objects.filter(ticker__id__in=followed_tickers).order_by('-date', '-time')

class GetTickerview(ListAPIView):
    serializer_class = TickerSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = AlertPAgination


class getTest(ListAPIView):
    serializer_class = AlertSerializer
    def get(self, request):
        list_alerts = []
        tick = Ticker.objects.get(symbol='AAPL')
        alert = GetRSIStrategy(ticker=tick, timespan='1day')
        if alert != None:
            list_alerts.append(alert)
            message = ''
        else:
            message = 'error'
        for alert in list_alerts:
            message += f'{alert['strategy']}_{alert['result_value']}_{alert['risk_level']}/ '
        
        return Response({"message":message},status=status.HTTP_200_OK)
    
        
    
#### endpoint to follow ticker ####
@api_view(['POST'])
def follow_ticker(request):
    try:
        profile = Profile.objects.get(user = request.user.pk)
        ticker_symbol = request.data["ticker_symbol"].strip().upper()
        ticker_id = (Ticker.objects.get(symbol=ticker_symbol)).pk
        if ticker_id in profile.followed_tickers:
            return Response({"message":f"you already follow ticker:{ticker_symbol}","followed ticker":profile.followed_tickers},status=status.HTTP_400_BAD_REQUEST)
        else :
            profile.followed_tickers.append(ticker_id)
            profile.save()
            return Response({"message":f"you followed ticker:{ticker_symbol}","followed ticker":profile.followed_tickers},status=status.HTTP_201_CREATED)

    except:
        return Response({"message":f"There is no ticker called:{ticker_symbol}"},status=status.HTTP_400_BAD_REQUEST)

#### endpoint to unfollow ticker ####
@api_view(['POST'])
def unfollow_ticker(request):
    try:
        profile = Profile.objects.get(user = request.user.pk)
        ticker_symbol = request.data["ticker_symbol"].strip().upper()
        try:
            profile.followed_tickers.remove((Ticker.objects.get(symbol=ticker_symbol)).pk)
            profile.save()
            return Response({"message":f"you unfollowed ticker:{ticker_symbol}","followed ticker":profile.followed_tickers},status=status.HTTP_201_CREATED)
        except:
            return Response({"message":f"you don't follow ticker:{ticker_symbol}","followed ticker":profile.followed_tickers},status=status.HTTP_400_BAD_REQUEST)

    except:
        return Response({"message":f"There is no ticker called:{ticker_symbol}"},status=status.HTTP_400_BAD_REQUEST)


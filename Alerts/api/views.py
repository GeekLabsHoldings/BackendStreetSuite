from Alerts.models import Alert , Result , Industry
from UserApp.models import Profile
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters , status
from rest_framework.generics import ListAPIView
from .serializer import AlertSerializer , FollowSerializer
from .paginations import AlertPAgination
from .filters import AlertFilters
from rest_framework.decorators import api_view
from Alerts.Scraping.ShortIntrestScraper import short_interest_scraper as shy
from Alerts.models import Ticker
from rest_framework.response import Response
from Alerts.Scraping.EarningsScraper import earning_scraping
from datetime import timedelta , date
import requests
from Alerts.tasks import getIndicator
from datetime import datetime as dt
from django.core.cache import cache
from Alerts.tasks import  earning30 
from Alerts.Scraping.TwitterScraper import twitter_scraper
from Alerts.Scraping.RedditScraper import Reddit_API_Response
from Alerts.tasks import earning15 , earning30
from Alerts.Strategies.RelativeVolume import GetRelativeVolume
from Alerts.Strategies.Earnings import GetEarnings as GEARN
from Alerts.consumers import WebSocketConsumer
from Alerts.Strategies.MajorSupport import GetMajorSupport
from Alerts.Strategies.UnusualOptionBuys import GetUnusualOptionBuys
from celery import group , chord
from  datetime import datetime
import time
#########################################################
################ Reddit Dependencies ####################
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import pytz
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import csv
#########################

## view list alerts ###
class AlertListView(ListAPIView):
    # permission_classes = [HasActiveSubscription]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    pagination_class = AlertPAgination
    filterset_class = AlertFilters
    search_fields = ['ticker__symbol']
    queryset = Alert.objects.all().order_by('-date','-time')
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


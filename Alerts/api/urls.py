from django.urls import path
from .views import (AlertListView  , FollowedAlertListView , Earnings  , MajorSupportTEST , rsi_1day, RedditScraper , follow_ticker , unfollow_ticker
                                ,ScrapTest , reduplication , test_reddit  , add_tickers , earny , mj , get_13f , tasks_1day , test_major )

urlpatterns = [
    path('', AlertListView.as_view() , name='list_alerts'),
    path('followed/', FollowedAlertListView.as_view() , name='list_followed_alerts'),
    # path('test/', test , name='test'),
    path('earn/', Earnings , name='earn'),
    path('MajorSupportTEST/', MajorSupportTEST , name='MajorSupportTEST'),
    path('rsi_1day/', rsi_1day , name='rsi_1day'),
    path('redditScraper/', RedditScraper, name='redditScraper'),
    path('test_scrap/', ScrapTest, name='test_scrap'),
    path('reduplication/', reduplication, name='reduplication'),
    path('test_reddit/', test_reddit, name='test_reddit'),
    # path('earn_scrap/', earn_scrap, name='earn_scrap'),
    path('add_tickers/', add_tickers, name='add_tickers'),
    path('earny/', earny, name='earny'),
    path('mj/', mj, name='mj'),
    path('get_13f/', get_13f, name='get_13f'),
    path('common/', tasks_1day, name='common'),
    path('test_major/', test_major, name='test_major'),
    path('follow_ticker/', follow_ticker, name='follow_ticker'),
    path('unfollow_ticker/', unfollow_ticker, name='unfollow_ticker'),
    
]

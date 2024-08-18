from django.urls import path
from .views import AlertListView , test , Earnings , short_interset , MajorSupportTEST , rsi_1day, RedditScraper

urlpatterns = [
    path('', AlertListView.as_view() , name='list_alerts'),
    path('test/', test , name='test'),
    path('earn/', Earnings , name='earn'),
    path('short_interset/', short_interset , name='short_interset'),
    path('MajorSupportTEST/', MajorSupportTEST , name='MajorSupportTEST'),
    path('rsi_1day/', rsi_1day , name='rsi_1day'),
    path('redditScraper/', RedditScraper, name='redditScraper'),
    
]

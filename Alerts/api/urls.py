from django.urls import path
from .views import (AlertListView  , FollowedAlertListView , getTest,
                    GetTickerview , follow_ticker , unfollow_ticker )

urlpatterns = [
    path('', GetTickerview.as_view() , name='list_alerts'),
    path('archived/', getTest.as_view() , name='list_alerts'),
    path('followed/', FollowedAlertListView.as_view() , name='list_followed_alerts'),
    path('follow_ticker/', follow_ticker, name='follow_ticker'),
    path('unfollow_ticker/', unfollow_ticker, name='unfollow_ticker'),
    
]

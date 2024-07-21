from django.urls import path
from .views import UserRankingView
urlpatterns = [

    path('', UserRankingView.as_view(), name="userranking")
]

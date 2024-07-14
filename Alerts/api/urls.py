from django.urls import path
from .views import Alerts_In_Day

urlpatterns = [
    path('', Alerts_In_Day , name='RSI-DAY'),
    # path('4hours/', RSI4hours , name='RSI-DAY'),
]

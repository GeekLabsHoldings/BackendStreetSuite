from django.urls import path
from .views import Alerts_In_Day , RSI4hours

urlpatterns = [
    path('', Alerts_In_Day , name='RSI-DAY'),
    path('hours/', RSI4hours , name='RSI-DAY'),
]

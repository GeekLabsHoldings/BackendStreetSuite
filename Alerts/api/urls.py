from django.urls import path
from .views import Alerts_In_Day , EMA_DAY , get_13f , RSI_4hour , RSI_1day , EMA_4HOUR , EMA_1HOUR, GetMentions , test , AlertListView

urlpatterns = [
    path('', AlertListView.as_view() , name='list_alerts'),
    path('ema1day/', EMA_DAY , name='ema'),
    path('ema4hour/', EMA_4HOUR , name='ema'),
    path('ema1hour/', EMA_1HOUR , name='ema'),
    path('13f/', get_13f , name='13f'),
    path('rsi4hours/', RSI_4hour , name='rsi4hours'),
    path('rsi1day/', RSI_1day , name='rsi1day'),
    path('mentions/', GetMentions.as_view() , name='mentions'),
    path('test/', test, name='test'),

]

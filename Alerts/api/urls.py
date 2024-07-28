from django.urls import path
from .views import   EMA_DAY , get_13f , RSI_4hour , RSI_1day , EMA_4HOUR , EMA_1HOUR  ,hh  , jojo  , AlertListView

urlpatterns = [
    path('', AlertListView.as_view() , name='list_alerts'),
    path('ema1day/', EMA_DAY , name='ema'),
    path('ema4hour/', EMA_4HOUR , name='ema'),
    path('ema1hour/', EMA_1HOUR , name='ema'),
    path('13f/', get_13f , name='13f'),
    path('rsi4hours/', RSI_4hour , name='rsi4hours'),
    path('rsi1day/', RSI_1day , name='rsi1day'),
    # path('vevo/', vevo, name='vevo'),
    path('jojo/', jojo, name='jojo'),
    path('hh/', hh, name='hh'),
    # path('earnings/', Earnings, name='earnings'),
]

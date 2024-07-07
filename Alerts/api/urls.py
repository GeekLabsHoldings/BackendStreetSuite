from django.urls import path
from .views import RSIoneDay , RSI4hours

urlpatterns = [
    path('', RSIoneDay , name='RSI-DAY'),
    path('4hours/', RSI4hours , name='RSI-DAY'),
]

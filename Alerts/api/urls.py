from django.urls import path
from .views import RSIoneDay

urlpatterns = [
    path('', RSIoneDay , name='RSI-DAY'),
]

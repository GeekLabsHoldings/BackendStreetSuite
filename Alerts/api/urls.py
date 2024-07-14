from django.urls import path
from .views import Alerts_In_Day

urlpatterns = [
    path('', Alerts_In_Day , name='RSI-DAY'),
<<<<<<< HEAD
    path('hours/', RSI4hours , name='RSI-DAY'),
=======
    # path('4hours/', RSI4hours , name='RSI-DAY'),
>>>>>>> 59e1ffd20ad101def87af2c429f05a1a8fcf4fad
]

from django.contrib import admin
from .models import Tickers , Alerts_Details, Ticker, Industry

admin.site.register(Tickers)
admin.site.register(Ticker)
admin.site.register(Industry)
admin.site.register(Alerts_Details)

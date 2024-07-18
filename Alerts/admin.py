from django.contrib import admin
from .models import Tickers , Alerts_Details, Ticker, Industry, Alert


class TickerAdmin(admin.ModelAdmin):
    list_display = ("id", 'symbol', 'name', 'industry')
class AlertAdmin(admin.ModelAdmin): 
    list_display = ('ticker',"strategy", "strategy_time", "strategy_value")
admin.site.register(Tickers)
admin.site.register(Ticker, TickerAdmin)
admin.site.register(Industry)
admin.site.register(Alerts_Details) 
admin.site.register(Alert, AlertAdmin)

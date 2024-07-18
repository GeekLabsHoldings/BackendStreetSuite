from django.contrib import admin
from .models import Tickers , Alerts_Details, Ticker, Industry, Alert

class AlertsAdmin(admin.ModelAdmin):
    list_display = ("ticker", "strategy", "value","risk_level","date","time","message")

class AlertAdmin(admin.ModelAdmin):
    list_display = ("ticker", "strategy", "strategy_time","strategy_value","risk_level","date","time")


class TickerAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'industry')
admin.site.register(Tickers)
admin.site.register(Ticker, TickerAdmin)
admin.site.register(Industry)
admin.site.register(Alerts_Details) 
admin.site.register(Alert , AlertAdmin)

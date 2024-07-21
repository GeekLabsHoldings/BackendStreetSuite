from django.contrib import admin
from .models import Tickers , Alerts_Details, Ticker, Industry, Alert , Rsi_Alert , EMA_Alert , Earning_Alert ,Alert_13F

class AlertsAdmin(admin.ModelAdmin):
    list_display = ("ticker", "strategy", "value","risk_level","date","time","message")

class AlertAdmin(admin.ModelAdmin):
    list_display = ("ticker", "strategy", "strategy_time","strategy_value","risk_level","date","time")


class TickerAdmin(admin.ModelAdmin):
    list_display = ("id", 'symbol', 'name', 'industry')
# class AlertAdmin(admin.ModelAdmin): 
#     list_display = ('ticker',"strategy", "strategy_time", "strategy_value")
admin.site.register(Tickers)
admin.site.register(Ticker, TickerAdmin)
admin.site.register(Industry)
admin.site.register(Rsi_Alert)
admin.site.register(EMA_Alert)
admin.site.register(Earning_Alert)
admin.site.register(Alert_13F)
admin.site.register(Alerts_Details , AlertsAdmin) 
admin.site.register(Alert , AlertAdmin)

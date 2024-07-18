from django.contrib import admin
from .models import Tickers , Alerts_Details, Ticker, Industry

class AlertsAdmin(admin.ModelAdmin):
    list_display = ("ticker", "strategy", "value","risk_level","date","time","message")

admin.site.register(Tickers)
admin.site.register(Ticker)
admin.site.register(Industry)
admin.site.register(Alerts_Details)

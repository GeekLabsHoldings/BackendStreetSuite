from django.contrib import admin
from .models import Tickers , Alerts_Details

class AlertsAdmin(admin.ModelAdmin):
    list_display = ("ticker", "strategy", "value","risk_level","date","time","message")

admin.site.register(Tickers)
admin.site.register(Alerts_Details,AlertsAdmin)

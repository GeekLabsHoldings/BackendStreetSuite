from django.contrib import admin
from .models import Tickers , Alerts_Details, Ticker, Industry , Rsi_Alert , EMA_Alert , Earning_Alert ,Alert_13F , Result, Alert_InsiderBuyer


#### classes for displaing each model in django admin pannel ###
class AlertsAdmin(admin.ModelAdmin):
    list_display = ("ticker", "strategy", "value","risk_level","date","time","message")

class AlertAdmin(admin.ModelAdmin):
    list_display = ("ticker", "strategy", "strategy_time","strategy_value","risk_level","date","time")

class ResultAdmin(admin.ModelAdmin):
    list_display = ("strategy", "time_frame","success","total")

class EarningAdmin(admin.ModelAdmin):
    list_display = ('ticker','strategy','strategy_time','Estimated_Revenue','Estimated_EPS' ,'currunt_IV' ,'Expected_Moves','earning_time' ,'date','time')

class IndustryAdmin(admin.ModelAdmin):
    list_display = ('type',)

class F13Admin(admin.ModelAdmin):
    list_display = ('investor_name','transaction_tybe','num_shares','ticker','ticker_price','amount_of_investment','date','time')
    
class EMAAdmin(admin.ModelAdmin):
    list_display = ('ticker','strategy','strategy_time','ema_value','risk_level','date','time')

class RSIAdmin(admin.ModelAdmin):
    list_display = ('ticker','strategy','strategy_time','rsi_value','risk_level','date','time')

class TickerAdmin(admin.ModelAdmin):
    list_display = ("id", 'symbol', 'name', 'industry')

class InsideBuyersAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'transaction_date', 'transaction_type', 'buyer_name')

### registering all models in alerts app ###
admin.site.register(Tickers)
admin.site.register(Ticker, TickerAdmin)
admin.site.register(Industry,IndustryAdmin)
admin.site.register(Rsi_Alert,RSIAdmin)
admin.site.register(EMA_Alert ,EMAAdmin)
admin.site.register(Earning_Alert , EarningAdmin)
admin.site.register(Alert_13F,F13Admin)
admin.site.register(Result , ResultAdmin)
admin.site.register(Alerts_Details , AlertsAdmin) 
# admin.site.register(Alert , AlertAdmin)
admin.site.register(Alert_InsiderBuyer , InsideBuyersAdmin)

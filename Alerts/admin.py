from django.contrib import admin
from .models import Ticker, Industry, Result, Alert


#### classes for displaing each model in django admin pannel ###
class AlertAdmin(admin.ModelAdmin):
    list_display = ("ticker", "strategy","time_posted")

class ResultAdmin(admin.ModelAdmin):
    list_display = ("strategy", "time_frame","success","total", "result_value")

class IndustryAdmin(admin.ModelAdmin):
    list_display = ('type',)
class TickerAdmin(admin.ModelAdmin):
    list_display = ("id", 'symbol', 'name', 'industry')


### registering all models in alerts app ###

admin.site.register(Ticker, TickerAdmin)
admin.site.register(Industry,IndustryAdmin)
admin.site.register(Result , ResultAdmin)
admin.site.register(Alert , AlertAdmin)


from django.contrib import admin
from .models import UserTrader, Trade
# Register your models here.

class TradeAdmin(admin.ModelAdmin):
    list_display = ('user_trader', 'symbol', 'date')
class UserTraderAdmin(admin.ModelAdmin):
    list_display = ('user', 'gain', 'win_streak_number')

admin.site.register(UserTrader , UserTraderAdmin)
admin.site.register(Trade , TradeAdmin)
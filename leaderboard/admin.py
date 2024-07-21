from django.contrib import admin
from .models import UserTrader
# Register your models here.


class UserTraderAdmin(admin.ModelAdmin):
    list_display = ('user', 'gain', 'win_streak_number')
admin.site.register(UserTrader , UserTraderAdmin)
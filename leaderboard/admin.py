from django.contrib import admin
from .models import UserRanking
# Register your models here.


class UserRankingAdmin(admin.ModelAdmin):
    list_display = ('user', 'gain', 'win_streak_number')
admin.site.register(UserRanking , UserRankingAdmin)
from django.contrib import admin
from .models import Tickers , Alerts_Details, Social_media_mentions

admin.site.register(Tickers)
admin.site.register(Alerts_Details)
admin.site.register(Social_media_mentions)

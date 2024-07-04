from Alerts.models import Tickers
from rest_framework import serializers

class RSISerializer(serializers.Serializer):
    message = serializers.CharField()
    ticker = serializers.CharField()
    RSI = serializers.FloatField()
    risk_level = serializers.CharField()

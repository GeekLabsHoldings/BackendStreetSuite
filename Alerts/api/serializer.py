from Alerts.models import Tickers
from rest_framework import serializers

class RSISerializer(serializers.Serializer):
    message = serializers.CharField()
    ticker = serializers.CharField()
    RSI = serializers.FloatField(required=False)
    EMA = serializers.FloatField(required = False)
    risk_level = serializers.CharField()

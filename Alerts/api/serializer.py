from Alerts.models import Tickers, Alerts_Details, Alert, Ticker
from rest_framework import serializers

class RSISerializer(serializers.Serializer):
    message = serializers.CharField(required=False)
    ticker = serializers.CharField(required=False)
    RSI = serializers.FloatField(required=False)
    EMA = serializers.FloatField(required = False)
    risk_level = serializers.CharField(required=False)

class TickersSerializer(serializers.Serializer):
    class Meta:
        model = Tickers
        fields = ["title"]


## serializer for alerts_details ##
class AlertsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alerts_Details
        exclude = ['id']

class TickerSerializer(serializers.Serializer):
    class Meta:
        model = Ticker
        exclude = ['id']

class AlertSerializer(serializers.ModelSerializer):
    ticker = TickerSerializer(required=False)
    class Meta:
        model = Alert
        exclude = ['id']
from Alerts.models import Tickers, Alerts_Details, Ticker , Alert, Industry
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
class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['type']

class TickerSerializer(serializers.ModelSerializer):
    industry = IndustrySerializer(read_only=True)
    class Meta:
        model = Ticker
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    ticker = TickerSerializer(read_only=True)
    class Meta:
        model = Alert
        fields = "__all__"

    
        
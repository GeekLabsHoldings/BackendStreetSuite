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

class TickerSerializer(serializers.ModelSerializer):
    # market_cap = serializers.SerializerMethodField()
    class Meta:
        model = Ticker
        fields = ["symbol", "name", "market_cap"]

    # def get_market_cap(self, instance):
    
    #     if instance.market_cap > 200000000000:
    #         return {"MEGA"} 
    #     elif instance.market_cap > 10000000000 and instance.market_cap <= 200000000000:
    #         return {"LARGE"} 
    #     elif instance.market_cap > 2000000000 and instance.market_cap <= 10000000000:
    #         return {"MEDUIM"} 
    #     elif instance.market_cap > 300000000 and instance.market_cap <= 2000000000:
    #         return {"SMALL"} 
    #     elif instance.market_cap > 50000000 and instance.market_cap <= 300000000:
    #         return {"MICRO"} 
    #     elif instance.market_cap < 50000000:
    #         return {"NANO"} 
class AlertSerializer(serializers.ModelSerializer):
    ticker = TickerSerializer(read_only=True)
    class Meta:
        model = Alert
        fields = "__all__"

    
        
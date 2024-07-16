from Alerts.models import Tickers, Social_media_mentions , Alerts_Details
from rest_framework import serializers

class RSISerializer(serializers.Serializer):
    message = serializers.CharField(required=False)
    ticker = serializers.CharField(required=False)
    RSI = serializers.FloatField(required=False)
    EMA = serializers.FloatField(required = False)
    risk_level = serializers.CharField(required=False)

class TickerSerializer(serializers.Serializer):
    class Meta:
        model = Tickers
        fields = ["title"]

class Social_media_mentions_Serializer(serializers.ModelSerializer):
    ticker = serializers.SerializerMethodField()
    
    class Meta:
        model = Social_media_mentions
        fields = ["ticker", "mentions", "date"]
    
    def get_ticker(self, obj):
        return obj.ticker.title
## serializer for alerts_details ##
class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alerts_Details
        exclude = ['id']
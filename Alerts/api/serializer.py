from Alerts.models import Tickers, Social_media_mentions
from rest_framework import serializers

class RSISerializer(serializers.Serializer):
    message = serializers.CharField(required=False)
    ticker = serializers.CharField(required=False)
    RSI = serializers.FloatField(required=False)
    EMA = serializers.FloatField(required = False)
    risk_level = serializers.CharField(required=False)

class TickerSerializer(serializers.Serializer):
    class meta:
        model = Tickers
        fields = ["title"]

class Social_media_mentions_Serializer(serializers.Serializer):
    ticker = TickerSerializer()
    
    class meta:
        model = Social_media_mentions
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['message'] = 'people are talking about this ticker, you might want to check it out'
        return representation
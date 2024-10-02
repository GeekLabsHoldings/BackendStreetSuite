from Alerts.models import Ticker , Alert, Industry, Result
from rest_framework import serializers

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
    

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'
    
### serialzer for follow ###
class FollowSerializer(serializers.Serializer):
    ticker_symbol = serializers.CharField()
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
    class Meta:
        model = Ticker
        fields = ["symbol", "name"]

    # def to_representation(self, instance):
      # Replace with your value to be checked

    # if value > 200000000000:
    #     print("Value is more than 200 billion.")

    # elif value > 10000000000 and value <= 200000000000:
    #     print("Value is more than 10 billion but less than or equal to 200 billion.")

    # elif value > 2000000000 and value <= 10000000000:
    #     print("Value is more than 2 billion but less than or equal to 10 billion.")

    # elif value > 300000000 and value <= 2000000000:
    #     print("Value is more than 300 million but less than or equal to 2 billion.")

    # elif value > 50000000 and value <= 300000000:
    #     print("Value is more than 50 million but less than or equal to 300 million.")

    # elif value < 50000000:
    #     print("Value is less than 50 million.")

class AlertSerializer(serializers.ModelSerializer):
    ticker = TickerSerializer(read_only=True)
    class Meta:
        model = Alert
        fields = "__all__"

    
        
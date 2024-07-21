from rest_framework import serializers
from leaderboard.models import UserTrader, Trade


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = '__all__'

class UserRankingsSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    trades = TradeSerializer(many=True, read_only=True)
    class Meta:
        model = UserTrader
        fields = '__all__'

    def get_user(self, obj):
        return {
            'first_name': obj.profile.user.first_name,
            'last_name': obj.profile.user.last_name,
            'username': obj.profile.user.username

        }
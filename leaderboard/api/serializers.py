from rest_framework import serializers
from leaderboard.models import UserTrader

class UserRankingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTrader
        fields = '__all__'
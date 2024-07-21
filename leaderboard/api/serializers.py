from rest_framework import serializers
from leaderboard.models import UserRanking

class UserRankingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRanking
        fields = '__all__'
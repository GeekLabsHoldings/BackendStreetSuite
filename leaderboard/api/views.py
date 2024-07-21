from rest_framework import generics
from leaderboard.models import UserRanking
from .serializers import UserRankingsSerializer

class UserRankingView(generics.ListAPIView):
    serializer_class = UserRankingsSerializer
    queryset = UserRanking.objects.all()

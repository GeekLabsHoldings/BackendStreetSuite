from rest_framework import generics
from leaderboard.models import UserTrader
from .serializers import UserRankingsSerializer

class UserRankingView(generics.ListAPIView):
    serializer_class = UserRankingsSerializer
    queryset = UserTrader.objects.all()

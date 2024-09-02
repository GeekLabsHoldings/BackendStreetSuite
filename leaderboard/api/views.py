from rest_framework import generics, filters
from leaderboard.models import UserTrader
from .serializers import UserRankingsSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

class UserRankingView(generics.ListAPIView):
    permission_classes = [IsAuthenticated] 
    serializer_class = UserRankingsSerializer
    queryset = UserTrader.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['trader_type']
    ordering_fields = ['total_profit', 'win_streak_number',' gain']

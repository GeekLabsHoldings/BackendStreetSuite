from rest_framework.decorators import api_view
from models import UserRankings
@api_view(["GET"])
def get_sorted_users(request):
    
    leaderboard = UserRankings.all().order_by("total_profit")
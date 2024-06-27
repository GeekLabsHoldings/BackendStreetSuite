from django.db import models
from django.contrib.auth.models import User

class UserRankings(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    total_profit = models.DecimalField(max_digits=32, decimal_places=2)
    gain = models.DecimalField(max_digits=5, decimal_places=2)
    number_of_trades = models.IntegerField()
    win_streak_number = models.IntegerField()
    day_streak = models.IntegerField()
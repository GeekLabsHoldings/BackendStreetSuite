from django.db import models
from django.contrib.auth.models import User

class UserRanking(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interactive_id = models.CharField(max_length=255)
    total_profit = models.DecimalField(max_digits=32, decimal_places=2)
    gain = models.DecimalField(max_digits=5, decimal_places=2)
    number_of_trades = models.IntegerField()
    win_streak_number = models.IntegerField()
    day_streak = models.IntegerField()  
from django.db import models
from django.contrib.auth.models import User
from UserApp.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserTrader(models.Model):
    Trader_Type_Choices = [
        ('DAY', 'Day'),
        ('SWING', 'Swing'),
        ('LONG', 'Long'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='users')
    interactive_id = models.CharField(max_length=255)
    trader_type = models.CharField(max_length=255, choices= Trader_Type_Choices)
    total_profit = models.DecimalField(max_digits=32, decimal_places=2)
    gain = models.DecimalField(max_digits=5, decimal_places=2)
    number_of_trades = models.IntegerField()
    win_streak_number = models.IntegerField()
    day_streak = models.IntegerField()

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

class Trade(models.Model):
    user_trader = models.ForeignKey(UserTrader, on_delete=models.CASCADE, related_name='trades')
    date = models.DateField(auto_now_add=True)
    symbol = models.CharField(max_length=255)
    symbol_id = models.CharField(max_length=255)
    share_quantity = models.IntegerField()
    price_per_share = models.FloatField()
    amount_paid = models.FloatField()
    side = models.CharField(max_length=2)

@receiver(post_save, sender=Trade)
def update_number_if_trades(sender, instance, created, **kwargs):
    if created:
        user_trader = instance.user_trader
        user_trader.number_of_trades = user_trader.number_of_trades +1
        user_trader.save()

    
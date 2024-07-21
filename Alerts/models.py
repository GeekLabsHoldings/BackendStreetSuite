from typing import Any
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
percentage_validators = [MinValueValidator(0), MaxValueValidator(100)]
class Tickers(models.Model):
    title = models.CharField(max_length=6)

    def __str__(self):
        return self.title
        
class PercentageOfRSI(models.Model):
    per_day = models.IntegerField(validators=percentage_validators, default=0)
    

## model for alerts ## 
class Alerts_Details(models.Model):
    ticker= models.CharField(max_length=8)
    strategy= models.CharField(max_length=50)
    value = models.FloatField(null=True, blank=True)
    risk_level = models.CharField(max_length=50, null=True, blank=True)
    date= models.DateField(auto_now_add=True)
    time= models.TimeField(auto_now_add=True)
    message = models.TextField(blank=True, null= True)

class Industry(models.Model):
    type = models.CharField(max_length=255)

    def __str__(self):
        return self.type
    
class Ticker(models.Model):
    symbol = models.CharField(max_length=9)
    name = models.CharField(max_length=255) 
    market_cap = models.FloatField()
    industry = models.ForeignKey(Industry, related_name="ticker",on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return self.symbol

class Alert(models.Model):
    ticker= models.ForeignKey(Ticker, related_name="alert", on_delete=models.CASCADE)
    strategy= models.CharField(max_length=50)
    strategy_time = models.CharField(max_length=5 , null=True , blank=True)
    strategy_value = models.FloatField(null=True , blank=True)
    risk_level = models.CharField(max_length=50, null=True)
    date= models.DateField(auto_now_add=True)
    time= models.TimeField(auto_now_add=True)

class Rsi_Alert(models.Model):
    ticker= models.ForeignKey(Ticker, related_name="rsi_alert", on_delete=models.CASCADE)
    strategy= models.CharField(max_length=50)
    strategy_time = models.CharField(max_length=5 , null=True , blank=True)
    rsi_value = models.FloatField(null=True , blank=True)
    risk_level = models.CharField(max_length=50, null=True)
    date= models.DateField(auto_now_add=True)
    time= models.TimeField(auto_now_add=True)

class EMA_Alert(models.Model):
    ticker= models.ForeignKey(Ticker, related_name="ema_alert", on_delete=models.CASCADE)
    strategy= models.CharField(max_length=50)
    strategy_time = models.CharField(max_length=5 , null=True , blank=True)
    ema_value = models.FloatField(null=True , blank=True)
    risk_level = models.CharField(max_length=50, null=True)
    date= models.DateField(auto_now_add=True)
    time= models.TimeField(auto_now_add=True)

## model for Earning Alert ##
class Earning_Alert(models.Model):
    ticker= models.ForeignKey(Ticker, related_name="earning_alert_ticker", on_delete=models.CASCADE)
    strategy= models.CharField(max_length=50)
    strategy_time = models.IntegerField()
    Estimated_Revenue = models.FloatField(null=True , blank=True)
    Estimated_EPS = models.FloatField(null=True , blank=True)
    currunt_IV = models.CharField(max_length=50 , null=True , blank= True)
    Expected_Moves = models.CharField(max_length=50 , null=True , blank=True)
    earning_time = models.CharField(max_length=50, null=True)
    date= models.DateField(auto_now_add=True)
    time= models.TimeField(auto_now_add=True)

## model for 13f strategy ##
class Alert_13F(models.Model):
    investor_name= models.CharField(max_length=100)
    transaction_tybe = models.CharField(max_length=50)
    num_shares = models.IntegerField()
    ticker= models.ForeignKey(Ticker, related_name="alert_13f_ticker", on_delete=models.CASCADE)
    ticker_price = models.FloatField()
    amount_of_investment = models.FloatField()
    date= models.DateField(auto_now_add=True)
    time= models.TimeField(auto_now_add=True)
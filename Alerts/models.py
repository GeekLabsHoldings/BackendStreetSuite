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
    value = models.FloatField()
    risk_level = models.CharField(max_length=50, null=True)
    date= models.DateField(auto_now_add=True)
    time= models.TimeField(auto_now_add=True)
    message = models.TextField(blank=True, null= True)

class Industry(models.Model):
    type = models.CharField(max_length=255)
    
class Ticker(models.Model):
    symbol = models.CharField(max_length=9)
    name = models.CharField(max_length=255) 
    market_cap = models.FloatField()
    industry = models.ForeignKey(Industry, related_name="ticker",on_delete=models.CASCADE, null=True, blank=True)

    
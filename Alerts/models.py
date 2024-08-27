from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Industry(models.Model):
    type = models.CharField(max_length=255)

    def __str__(self):
        return self.type
    
class Ticker(models.Model):
    symbol = models.CharField(max_length=9)
    name = models.CharField(max_length=255) 
    market_cap = models.FloatField()
    market_capital = models.CharField(max_length=255, blank=True, null=True)
    industry = models.ForeignKey(Industry, related_name="ticker",on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return self.symbol
    
    def save(self, *args, **kwargs):
        if self.market_cap > 200000000000:
            self.market_capital = "Mega"

        if self.market_cap > 10000000000 and self.market_cap <= 200000000000:
            self.market_capital = "Large" 

        if self.market_cap > 2000000000 and self.market_cap <= 10000000000:
            self.market_capital = "Medium"  

        if self.market_cap > 300000000 and self.market_cap <= 2000000000:
            self.market_capital = "Small"  

        if self.market_cap > 50000000 and self.market_cap <= 300000000:
            self.market_capital = "Micro" 

        if self.market_cap < 50000000:
            self.market_capital = "Nano"
            
        super().save(*args, **kwargs)

class Alert(models.Model):
    ## common in RSI & EMA & Relative volume & web scraper ##
    ticker= models.ForeignKey(Ticker, related_name="alert", on_delete=models.CASCADE)
    strategy= models.CharField(max_length=50)
    time_frame = models.CharField(max_length=10 , null=True , blank=True)
    result_value = models.FloatField(null=True , blank=True)
    risk_level = models.CharField(max_length=50, null=True , blank=True)
    ## Earning ##
    Estimated_Revenue = models.FloatField(null=True , blank=True)
    Estimated_EPS = models.FloatField(null=True , blank=True)
    current_IV = models.CharField(max_length=50 , null=True , blank= True)
    Expected_Moves = models.CharField(max_length=50 , null=True , blank=True)
    earning_time = models.CharField(max_length=50, null=True , blank=True)
    ## 13 f ##
    investor_name= models.CharField(max_length=100, null=True , blank=True) 
    transaction_type = models.CharField(max_length=50, null=True , blank=True)
    shares_quantity = models.IntegerField( null=True , blank=True)
    ticker_price = models.FloatField(null=True , blank=True)
    amount_of_investment = models.FloatField(null=True , blank=True)
    ## Insider buyer ##
    transaction_date = models.DateField(null=True , blank=True)
    job_title = models.CharField(max_length=255, null=True , blank=True)
    filling_date = models.CharField(max_length=255, null=True , blank=True)
    ## coomon date ##
    time_posted = models.DateTimeField(auto_now_add=True , null=True, blank=True)
    date = models.DateField(auto_now_add=True , null=True, blank=True)
    time= models.TimeField(auto_now_add=True , null=True, blank=True)
    current_price = models.FloatField(null=True , blank=True)

    ## to prevent dublication ##
    class Meta:
        unique_together = ['ticker','strategy','result_value','time_posted']

## model for result ##
class Result(models.Model):
    strategy = models.CharField(max_length=50)
    time_frame = models.CharField(max_length=50, blank=True, null=True)
    success = models.IntegerField( default=0)
    total = models.IntegerField(default=0)
    result_value = models.FloatField(default=0.0)
        
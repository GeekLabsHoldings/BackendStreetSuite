from django.db import models

class Tickers(models.Model):
    title = models.CharField(max_length=6)

    def __str__(self):
        return self.title
        
    

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
    ticker= models.ForeignKey(Ticker, related_name="alert", on_delete=models.CASCADE)
    strategy= models.CharField(max_length=50)
    strategy_time = models.CharField(max_length=5 , null=True , blank=True)
    strategy_value = models.FloatField(null=True , blank=True)
    risk_level = models.CharField(max_length=50, null=True)
    date= models.DateField(auto_now_add=True)
    time= models.TimeField(auto_now_add=True)

## model for result ##
class Result(models.Model):
    strategy = models.CharField(max_length=50)
    time_frame = models.CharField(max_length=50)
    success = models.IntegerField(null=True, blank=True)
    total = models.IntegerField(null=True, blank=True)

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
#Insider buyer
class Alert_InsiderBuyer(models.Model):
    ticker= models.ForeignKey(Ticker, related_name="Insiderbuyers", on_delete=models.CASCADE)
    transaction_date = models.DateField()
    strategy_name = models.CharField(max_length=255, null=True , blank=True)
    transaction_type = models.CharField(max_length=15, null=True , blank=True)
    buyer_name = models.CharField(max_length=100, null=True , blank=True)
    job_title = models.CharField(max_length=255, null=True , blank=True)
    share_quantity = models.IntegerField()
    price_per_share = models.FloatField()
    filling_date = models.CharField(max_length=255, null=True , blank=True)
    date= models.DateField(auto_now_add=True, null=True , blank=True )
    time= models.TimeField(auto_now_add=True, null=True , blank=True)


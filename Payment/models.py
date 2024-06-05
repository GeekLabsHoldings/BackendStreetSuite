from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    title = models.CharField(max_length=17)
    price = models.FloatField()
    description = models.TextField()
class UserPayment(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, blank=True, null=True)
    cvv = models.CharField(max_length=3, blank=True, null=True, help_text='Enter the CVV/CVC code')
    card_name = models.CharField(max_length=14, blank=True, null=True)
    expiry_month = models.IntegerField(max_length=2, blank=True, null=True)
    expiry_year = models.IntegerField(max_length=2, blank=True, null=True)
    month_paid = models.BooleanField(default=False)
    week_paid = models.BooleanField(default=False)
    free_trial = models.BooleanField(default=False)
    product = models.OneToOneField(Product, blank=True, null=True, on_delete=models.CASCADE)


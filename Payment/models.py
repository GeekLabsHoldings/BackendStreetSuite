from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserPayment(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, blank=True, null=True)
    cvv = models.CharField(max_length=3, blank=True, null=True)
    card_name = models.CharField(max_length=14, blank=True, null=True)
    expiry_date = models.DateField(max_length=5, blank=True, null=True)
    month_paid = models.BooleanField(default=False)
    week_paid = models.BooleanField(default=False)
    free_trial = models.BooleanField(default=False)
from django.db import models
from django.contrib.auth.models import User
# Create your models here.



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    About = models.TextField(blank=True, max_length=300)
    Phone_Number = models.CharField(max_length=12, blank=True)




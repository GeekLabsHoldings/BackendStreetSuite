from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Review(models.Model):
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)
    reivew_text = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)
    show = models.BooleanField(default=True)
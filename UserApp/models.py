from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        Profile.objects.create(user=instance)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    About = models.TextField(blank=True, max_length=300)
    Phone_Number = models.CharField(max_length=12, blank=True)
    image = models.ImageField(upload_to="ProfilePic/", default="ProfilePic/Default.jpg")
    is_admin = models.BooleanField(default=False)




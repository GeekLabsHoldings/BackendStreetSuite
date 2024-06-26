from django.db import models

class ChangeLog(models.Model):
    message = models.TextField()
    date = models.DateField(auto_now=True)

class Message(models.Model):
    text_message = models.TextField()
    date = models.DateField(auto_now=True)
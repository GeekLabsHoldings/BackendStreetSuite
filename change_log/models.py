from django.db import models

class ChangeLog(models.Model):
    message = models.TextField()

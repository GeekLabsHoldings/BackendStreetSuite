from django.db import models

class ChangeLog(models.Model):
    message = models.TextField()
    date = models.DateField(auto_now=True)

    def __str__(self):
        return self.message

class Message(models.Model):
    text_message = models.TextField()
    date = models.DateField(auto_now=True)

    def __str__(self):
        return self.text_message
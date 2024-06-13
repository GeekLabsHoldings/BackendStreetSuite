from django.db import models

class ContactMessage(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    message = models.TextField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

from typing import Any
from django.db import models

class Tickers(models.Model):
    title = models.CharField(max_length=6)

    def __str__(self):
        return self.title
        

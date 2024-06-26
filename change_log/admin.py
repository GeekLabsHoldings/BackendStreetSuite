from django.contrib import admin
from .models import ChangeLog , Message
# Register your models here.
admin.site.register(ChangeLog)
admin.site.register(Message)
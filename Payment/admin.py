from django.contrib import admin
from .models import Product, UserPayment
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display =  ("title", 'amount')
    
admin.site.register(Product, ProductAdmin)
admin.site.register(UserPayment)
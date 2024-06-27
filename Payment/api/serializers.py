from rest_framework import serializers
from Payment.models import UserPayment, Product

from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        

class UserPaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = UserPayment
        fields = ['user', 'product', 'stripe_customer_id']
    
    def get_user(self, obj):
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'email': obj.user.email
        }
    
    
    

class ProductSerializer(serializers.ModelSerializer):
    checkout_url = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'price_id', 'title', 'amount', 'description', 'checkout_url']
        
    def get_checkout_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'checkout/{obj.id}/')
        return None
        
class CheckoutSerializer(serializers.Serializer):
    price_id = serializers.CharField(max_length=100)

        
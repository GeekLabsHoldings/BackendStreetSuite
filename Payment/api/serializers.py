from rest_framework import serializers
from Payment.models import UserPayment, Product
from django.contrib.auth.models import User
import datetime
import re

def validate_expiry_year(value):
    today = datetime.datetime.now()
    year = value+2000
    if year < today.year: 
        raise serializers.ValidationError("Expiry date cannot be in the past.")  
def validate_expiry_month(value):
    if not 1 <= value <= 12:
        raise serializers.ValidationError("Month must be between 1 and 12.")
def check_cvc(value):
    if not 3 <= len(value) <= 4:
        raise serializers.ValidationError(" cvc/cvv number must be 3 or 4 digits.")
    
class UserPaymentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserPayment
        fields = '__all__'
    
    cvc = serializers.CharField(
        required=True,
        validators=[check_cvc],
    )
    expiry_year = serializers.IntegerField(
        required=True,
        validators=[validate_expiry_year]
    )
    expiry_month = serializers.IntegerField(
        required=True,
        validators=[validate_expiry_month]
    )
    card_number = serializers.IntegerField(required=True)

    def to_representation(self, instance):
        from UserApp.api.serializers import UserSerializer
        
        ret = super().to_representation(instance)
        # ret['user'] = UserSerializer(instance.user).data 
        # return ret
        if isinstance(instance, UserPayment):
            user = instance.user
            # Adding user details to the representation
            ret['user'] = {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        elif isinstance(instance, dict):
            # Handle the case where instance is a dictionary
            user_id = instance.get('user.id')
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    ret['user'] = {
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                except User.DoesNotExist:
                    ret['user'] = None
        return ret
    
    def get_user(self, obj):
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'email': obj.user.email
        }
    

class ProductSerializer(serializers.ModelSerializer):
    # checkout = serializers.HyperlinkedIdentityField(
    #     view_name='checkout',
    #     lookup_field= 'pk',
    #     read_only=True
    # )
    class Meta:
        model = Product
        # fields = '__all__'
        fields = ['id', 'title', 'price', 'description']
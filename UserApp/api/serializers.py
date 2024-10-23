from rest_framework import serializers
from UserApp.models import User, Profile
from UserApp.models import EmailVerification
import random
import string
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['Token'] = 'Token'
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        if hasattr(user, 'userpayment'): 
            user_payment = user.userpayment          
            token['payment_method_id'] = user_payment.payment_method_id
            if user_payment.product:
                product = user_payment.product
                token['product_title'] = product.title
                token['product_amount'] = str(product.amount) 
        return token


## serializer for google login and signup ##
class GoogleSerilaizer(serializers.Serializer):
    name = serializers.CharField()
    given_name = serializers.CharField()
    family_name = serializers.CharField()
    email = serializers.EmailField()
    picture = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url    
        else:
            return None


### serializer for change password ###
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    password_confirmation = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['password_confirmation']:
            raise serializers.ValidationError({"message":"Passwords do not match"})
        return data 

class RegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=50)
    password2 = serializers.CharField(max_length=50)
    phone_number = serializers.CharField()

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"message":"Passwords do not match"})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"message":"Email account is already exists"})
        return data
    
    def create(self, validated_data):
        email = validated_data['email']
        # Send verification email to the user
        send_verification_email(email , first_name=validated_data['first_name'] , 
                                last_name=validated_data['last_name'] ,
                                  password=validated_data['password'] ,
                                  phone_number=validated_data['phone_number'])

        return validated_data

def send_verification_email(email , first_name = None , last_name = None , password = None , phone_number=None):
    verification_code = ''.join(random.choices( string.digits, k=6))
    try:
        verification = EmailVerification.objects.get(email=email)
        verification.verification_code = verification_code
        verification.first_name = first_name
        verification.last_name = last_name
        verification.password = password
        verification.phone_number = phone_number
        verification.save()
    except EmailVerification.DoesNotExist:
        verification = EmailVerification.objects.create(email=email,
                                            verification_code=verification_code ,
                                            first_name = first_name ,
                                            last_name = last_name ,password = password,phone_number=phone_number)
    send_mail(
        'Verify your email',
        f'Your verification code is {verification_code}',
        'streetsuits0@gmail.com',
        [email],
        fail_silently=False,
    )
    return verification_code

#### serializer for forgetting password ####
class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        if not User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email account does not exist in the system")
        return data  
    
    def create(self, validated_data):
        email = validated_data['email']
        self.email = email
        # Handle EmailVerification object
        try:
            object_verification = EmailVerification.objects.get(email=email)
            object_verification.delete()
        except EmailVerification.DoesNotExist:
            pass 
        send_verification_email(email=email)
        return validated_data

### verification serializer for forget password ####
class VerificationForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            verification = EmailVerification.objects.get(
                verification_code=data['verification_code']
            )
            email = data['email']
            if email:
                user = User.objects.get(email=email)
                if not verification.email == user.email:
                    raise serializers.ValidationError({"message":"not valid verification code"})
            else:
                raise serializers.ValidationError({"message":"email needed"})
                
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError({"message":"Invalid verification code"})
        return data

    def create(self, validated_data):
        verification = EmailVerification.objects.get(
            # email=validated_data['email'],
            verification_code=validated_data['verification_code']
        )
        token = self.context.get('token')  # Retrieve token from context
        verification.delete()  # Remove verification record once user is created
        return verification

### verificaton serializer for sign up process ###
class VerificationSerializer(serializers.Serializer):
    # email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            verification = EmailVerification.objects.get(
                verification_code=data['verification_code']
            )
            email = verification.email
         
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid verification code")
        return data

    def create(self, validated_data):
        verification = EmailVerification.objects.get(
            # email=validated_data['email'],
            verification_code=validated_data['verification_code']
        )
        
        user = User.objects.create_user(
            username=verification.email.split('@')[0],
            email=verification.email,
            password=verification.password,
            first_name=verification.first_name,
            last_name=verification.last_name
        )
        profile = Profile.objects.get(use=user)
        profile.Phone_Number = verification.phone_number
        verification.delete()  # Remove verification record once user is created
        return verification

### reste password serializer for forgot user ###
class ResetForgetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField() 
    password_confirmation = serializers.CharField() 
    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError({"message":"Passwords do not match"})
        return data
    def create(self, validated_data):
        email = self.context.get('email')
        if email:
            user = User.objects.get(email=email)
            user.set_password(validated_data['password'])
            user.save()
            return validated_data    
        else:
            raise serializers.ValidationError({"message":"email needed please !"})

### reste password serializer for forgot user ###
class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField() 
    password_confirmation = serializers.CharField() 

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError({"message":"Passwords do not match"})
        return data
    def create(self, validated_data):
        user = self.context.get('user')
        user.set_password(validated_data['password'])
        user.save()
        return validated_data    

class UserSerializer(serializers.ModelSerializer):
    
    password_confirmation = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [ 'username','email', 'first_name', 'last_name', 'password', 'password_confirmation']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            },
        }
        
    def update(self, instance, validated_data):
        # Update user and profile
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.save()

        return instance

    def save(self):
        password = self.validated_data['password']
        password_confirmation = self.validated_data['password_confirmation']
        if password != password_confirmation:
            raise serializers.ValidationError('Passwords do not match.')
        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError('email is already exists')

        account = User(email=self.validated_data['email'], username=self.validated_data['username'])
        account.first_name = self.validated_data['first_name']
        account.last_name = self.validated_data['last_name']

        account.set_password(password)
        account.save()

        return account
    

### serializer for profile settings ###
class ProfileSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['id','user','is_admin']

### serializer for user for profile settings ###
class UserProfileSettingsSerializer(serializers.ModelSerializer):
    profile = ProfileSettingsSerializer()
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name','last_name','email','profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile
        # Update user instance
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()

        # Update profile instance
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance
    

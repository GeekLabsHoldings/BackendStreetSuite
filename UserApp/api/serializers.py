from rest_framework import serializers
from rest_framework.reverse import reverse
from UserApp.models import User, Profile
from UserApp.models import EmailVerification
import random
import string
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.authtoken.models import Token

class RegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=50)
    password2 = serializers.CharField(max_length=50)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match")
        # if not data['email'].endswith('@gmail.com'):
        #     raise serializers.ValidationError("Email must be a Gmail account")
        # if User.objects.get(email=data['email']):
        #     raise serializers.ValidationError("Email account is already exists")
        return data
    
    def create(self, validated_data):
        email = validated_data['email']
        # Send verification email to the user
        send_verification_email(email , first_name=validated_data['first_name'] , last_name=validated_data['last_name'] , password=validated_data['password'])

        return validated_data

def send_verification_email(email , first_name = None , last_name = None , password = None):
    verification_code = ''.join(random.choices( string.digits, k=6))
    EmailVerification.objects.create(email=email,
                                        verification_code=verification_code ,
                                        first_name = first_name ,
                                        last_name = last_name ,password = password)
    send_mail(
        'Verify your email',
        f'Your verification code is {verification_code}',
        'your-email@example.com',
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
        user = User.objects.get(email=email)
        token , created = Token.objects.get_or_create(user=user)
        print(token.key)
        self.token = token.key
        print(self.token) 
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
    # email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            verification = EmailVerification.objects.get(
                verification_code=data['verification_code']
            )
            token = self.context.get('token')
            if token:
                user = Token.objects.get(key=token).user
                if not verification.email == user.email:
                    raise serializers.ValidationError({"message":"not valid verification code"})
            else:
                raise serializers.ValidationError({"message":"token needed"})
                
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError({"message":"Invalid verification code"})
        return data

    def create(self, validated_data):
        verification = EmailVerification.objects.get(
            # email=validated_data['email'],
            verification_code=validated_data['verification_code']
        )
        token = self.context.get('token')  # Retrieve token from context
        print(f'token::{token}')
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
        token = self.context.get('token')
        if token:
            print(f'token==={token}')
            user = Token.objects.get(key= token).user
            print(user.password)
            user.set_password(validated_data['password'])
            print(user.password)
            user.save()
            return validated_data    
        else:
            raise serializers.ValidationError({"message":"token needed please !"})

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
        # instance.username = validated_data.get('username', instance.username)
        # instance.email = validated_data.get('email', instance.email)
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
        print(account.password)
        account.set_password("1223344")
        print(account.password)
        account.save()

        return account
    
class ProfileSerializer(serializers.ModelSerializer):
    
    user = UserSerializer()
    class Meta:
        model = Profile
        fields = ['user','About', 'Phone_Number']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        
        # Update the User instance
        if user_data:
            user = instance.user
            user.username = user_data.get('username', user.username)
            # user.email = user_data.get('email', user.email)
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()

        # Update the Profile instance
        instance.About = validated_data.get('About', instance.About)
        instance.Phone_Number = validated_data.get('Phone_Number', instance.Phone_Number)
        instance.save()

        return instance
    
    def to_representation(self, instance):
        from BlogApp.api.serializers import PostListSerializer 
        representation = super().to_representation(instance)
        user_posts = instance.user.posts.all()
        posts_data = []
        request = self.context.get('request')
        for post in user_posts:
            post_data = PostListSerializer(post, context={'request': request}).data
            post_data['url'] = reverse('post-detail', kwargs={'slug': post.slug}, request=request)
            posts_data.append(post_data)
        representation['posts'] = posts_data
        return representation
    
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
        # exclude = ['id']
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
    

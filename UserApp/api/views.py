from rest_framework import status , generics
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from UserApp.models import Profile , EmailVerification
from UserApp.api.serializers import  (UserSerializer, ChangePasswordSerializer, ProfileSerializer,UserProfileSettingsSerializer,ProfileSettingsSerializer ,
                                      ResetForgetPasswordSerializer, VerificationForgetPasswordSerializer ,VerificationSerializer ,
                                        RegistrationSerializer , ForgetPasswordSerializer , GoogleSerilaizer)
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from django.contrib.auth.models import User
#### auth ####
from django.conf import settings
from django.shortcuts import redirect 
from django.views.generic.base import View
from django.contrib.auth import authenticate

### endpoint for change password ###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    serializer = ChangePasswordSerializer(data= request.data)
    if serializer.is_valid():
        password = request.data['old_password']
        if user.check_password(password):
            user.set_password(request.data['new_password'])
            user.save()
            return Response({"message":"password changed successfully"})
        else:
            return Response({"message":"old password not correct"})
    else:
        return Response({"message":"new password not equal password confirmation"})

### endpoint for resgisteration ###
class SignUpView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(    
                {"message": "The verification code has been sent to your email."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors)

## end point for verification on sign up ##
# class VerificationView(generics.CreateAPIView):
class VerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = VerificationSerializer(data=request.data)
        if serializer.is_valid():
            verification_code = request.data.get('verification_code')
            try:
                verification = EmailVerification.objects.get(verification_code=verification_code)
                user = User.objects.create_user(
                    username=verification.email.split('@')[0],
                    email=verification.email,
                    password=verification.password,
                    first_name=verification.first_name,
                    last_name=verification.last_name
                )
                profile = Profile.objects.get(user=user)
                profile.Phone_Number = verification.phone_number
                profile.save()
                verification.delete()  # Remove verification record once user is created
                return Response(
                    {"message": "User created successfully."},
                    status=status.HTTP_201_CREATED
                )
            except EmailVerification.DoesNotExist:
                return Response(
                    {"message": "Invalid verification code."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

## enpoint for goofle login and sign up ##
@api_view(['POST'])
def google_login(request):
    serializer = GoogleSerilaizer(data=request.data)
    if serializer.is_valid():
        ## check if login or sign up ##
        try:
            email = request.data['email'].strip()
            user = User.objects.get(email=email)
            token , created= Token.objects.get_or_create(user=user)
            return Response({'message':'loged in successfully!','token':token.key})
        except User.DoesNotExist:
            username = request.data['name']
            first_name = request.data['given_name']
            last_name = request.data['family_name']
            image = request.data['picture']
            email = request.data['email']
            user = User.objects.create(username=username , first_name=first_name, last_name=last_name , email=email)
            user.save()
            profile = Profile.objects.get(user=user)
            profile.image = image
            profile.save()
            token , created = Token.objects.get_or_create(user=user)
            return Response({"message":"sign up successfully!","token":token.key})



### endpoint for forget password ###
class ForgetPassword(generics.CreateAPIView):
    serializer_class = ForgetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            token = getattr(serializer, 'token' , None)
            return Response({"message":"the verification code has been sent to your email!","token":token})
        else:
            return Response(
                {"message": "the email yo have sent is not in the system please sign up first!"},
                status=status.HTTP_400_BAD_REQUEST
            )

### verify forget password verification code ###
class VerifyForgetPasswordView(generics.CreateAPIView):
    serializer_class = VerificationForgetPasswordSerializer

    def create(self, request, *args, **kwargs):
        token = request.headers.get('Authorization')
        if token:
            token = token.split(' ')[1]
        serializer = self.get_serializer(data=request.data, context={'request': request, 'token': token})
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"message": "correct verification code"},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": "please enter the valid verification code !"},
                status=status.HTTP_400_BAD_REQUEST)

### reset password for user forgot password ###
class ResetPasswordView(generics.CreateAPIView): 
    serializer_class = ResetForgetPasswordSerializer

    def create(self, request, *args, **kwargs):
        token = request.headers.get('Authorization')
        if token:
            token = token.split(' ')[1]
        serializer = self.get_serializer(data=request.data, context={'request': request, 'token': token})
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"message": "password reset process done!"},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','POST',])
def RegistrationView(request):
    if request.method == 'GET':
        pass
    if request.method == 'POST':
        data = request.data.copy()
        email = data['email']
        username , tail = email.split("@")
        data['username'] = username



        serializer = UserSerializer(data=data)  
        data = {}

        if serializer.is_valid():
            account = serializer.save()
        #     data['response'] = "successfully registered"
        #     data['username'] = account.username
        #     data['email'] = account.email
        #     data['first_name'] = account.first_name
        #     data['last_name'] = account.last_name
        #     token = Token.objects.get(user=account).key
        #     data['token'] = token
        else:
            data = serializer.errors
        
        return Response(data)

@api_view(['POST',])
def logout(request):
    if request.method == 'POST':
        request.user.auth_token.delete()
        return Response({'Response' : 'logout successfully'})
    
@api_view(['GET', 'PATCH',])
@permission_classes([IsAuthenticated])
def ProfileView(request, pk):
    profile = Profile.objects.get(pk=pk)

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
    if request.method == 'PATCH':
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400)

@api_view(['POST'])
def log_in(request):
    data = request.data.copy()
    email = data['email'].strip()
    password = data['password']
    try:
        user = User.objects.get(email=email)
        username = user.username
        user2 = authenticate(username=username , password=password)
        if user2:
            token , created= Token.objects.get_or_create(user=user)
            return Response({"message":"loged in successfully!","token":token.key},status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message':'wrong password'},status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"message":"your email not exists in the website"},status=status.HTTP_404_NOT_FOUND)
    
### profile settings endpoint ###
class ProfileSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSettingsSerializer
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        profile = Profile.objects.get(user=user)
        return profile

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        

### profile settings endpoint ###
@api_view(['PATCH','GET'])
def profileSettingsView(request):
    user = request.user

    if request.method == 'GET':
        profile = Profile.objects.get(user=user)
        serializer = UserProfileSettingsSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        user = request.user
        profile = Profile.objects.get(user=user)
        
        serializer = UserProfileSettingsSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            _update_user_and_profile(user, profile, serializer.validated_data)
            return Response({"data":serializer.data,"message": "Updated successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
def _update_user_and_profile(user, profile, validated_data):
    profile_data = validated_data.pop('profile', {})
    
    # Update user instance
    user.username = validated_data.get('username', user.username)
    user.first_name = validated_data.get('first_name', user.first_name)
    user.last_name = validated_data.get('last_name', user.last_name)
    user.email = validated_data.get('email', user.email)
    if 'password' in validated_data:
        user.set_password(validated_data['password'])
    user.save()

    # Update profile instance
    for attr, value in profile_data.items():
        setattr(profile, attr, value)
    profile.save()

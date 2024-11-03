from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from UserApp.models import Profile, EmailVerification
from UserApp.api.serializers import  (ChangePasswordSerializer,ResetForgetPasswordSerializer,VerificationForgetPasswordSerializer,
                                      VerificationSerializer, RegistrationSerializer, ForgetPasswordSerializer, GoogleSerilaizer, ProfileSettingsSerializer)
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomTokenObtainPairSerializer
from datetime import timedelta
import random, string
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

def generate_random_suffix(length=2):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# class VerificationView(generics.CreateAPIView):
class VerificationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = VerificationSerializer(data=request.data)
        if serializer.is_valid():
            verification_code = request.data.get('verification_code')
            try:
                verification = EmailVerification.objects.get(verification_code=verification_code)
                username = verification.email.split('@')[0]
                if User.objects.filter(username=username).exists():
                    base_username = username
                    username = base_username + '_' + generate_random_suffix()
                user = User.objects.create_user(
                    username=username,
                    email=verification.email,
                    password=verification.password,
                    first_name=verification.first_name,
                    last_name=verification.last_name
                )
                profile = Profile.objects.get(user=user)
                profile.Phone_Number = verification.phone_number
                profile.save()
                # Remove verification record once user is created
                verification.delete()  
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

## enpoint for google login and sign up ##
@api_view(['POST'])
def google_login(request):
    serializer = GoogleSerilaizer(data=request.data)
    if serializer.is_valid():
        ## check if login or sign up ##
        try:
            email = request.data['email'].strip()
            user = User.objects.get(email=email)
            refresh =CustomTokenObtainPairSerializer.get_token(user)
            access = refresh.access_token
            return Response({"message":"logged in successfully!",
                             "Token":str(access)},
                             status=status.HTTP_202_ACCEPTED)
        except User.DoesNotExist:
            # Took the user data from the client server and create a new user and return the token
            name = request.data['name']
            image = request.data['picture']
            email = request.data['email']
            first_name, last_name = name.split()
            username = email.split('@')[0]
            user = User.objects.create(username=username , first_name=first_name, last_name=last_name , email=email)
            user.save()
            profile = Profile.objects.get(user=user)
            profile.image = image
            profile.save()
            refresh =CustomTokenObtainPairSerializer.get_token(user)
            access = refresh.access_token
            return Response({"message":"logged in successfully!",
                             "Token":str(access)},
                             status=status.HTTP_202_ACCEPTED)
        
# Normal Login
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
            refresh = CustomTokenObtainPairSerializer.get_token(user)
            access = refresh.access_token
            return Response({"message":"logged in successfully!",
                             "Token":str(access)},
                             status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message':'wrong password'},
                            status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"message":" your email not exists in the website "},status=status.HTTP_404_NOT_FOUND)

#logging Out 
@api_view(['POST',])
def logout(request):
    user = request.user
    refresh = RefreshToken.for_user(user)
    # Setting the expiration date of the access and the refresh token expire in 10 seconds
    refresh.set_exp(lifetime=timedelta(seconds=5)) 
    access = refresh.access_token
    access.set_exp(lifetime=timedelta(seconds=5)) 
    return Response({"message":"logged out successfully!"},
                         status=status.HTTP_200_OK)
### endpoint for forget password ###
class ForgetPassword(generics.CreateAPIView):
    serializer_class = ForgetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            email = getattr(serializer, 'email' , None)
            return Response({"message":"the verification code has been sent to your email!","email":email})
        else:
            return Response(
                {"message": "the email yo have sent is not in the system please sign up first!"},
                status=status.HTTP_400_BAD_REQUEST
            )

### verify forget password verification code ###
class VerifyForgetPasswordView(generics.CreateAPIView):
    serializer_class = VerificationForgetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"message": "correct verification code","email":request.data['email']},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": "please enter the valid verification code !"},
                status=status.HTTP_400_BAD_REQUEST)

### reset password for user forgot password ### 
class ResetForgetPasswordView(generics.CreateAPIView): 
    serializer_class = ResetForgetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
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
        
           
### profile settings endpoint ###
@api_view(['PATCH','GET'])
def profileSettingsView(request):
    user = request.user
    ## show all profile data of user ##
    if request.method == 'GET':
        serializer = ProfileSettingsSerializer(user.profile)
        return Response(serializer.data)
    ## update data of user prfile ##
    elif request.method == 'PATCH':
        serializer = ProfileSettingsSerializer(user.profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"message": "Updated successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        

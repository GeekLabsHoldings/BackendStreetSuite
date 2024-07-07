from rest_framework import status , generics
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from UserApp.models import Profile , EmailVerification
from UserApp.api.serializers import  UserSerializer, ChangePasswordSerializer, ProfileSerializer,UserProfileSettingsSerializer,ProfileSettingsSerializer ,ResetForgetPasswordSerializer, VerificationForgetPasswordSerializer ,VerificationSerializer , RegistrationSerializer , ForgetPasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from django.contrib.auth.models import User
#### auth ####
from django.conf import settings
from django.shortcuts import redirect 
from django.views.generic.base import View
from django.contrib.auth import authenticate

### endpoint for change password ###
@api_view(['PUT','PATCH'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    serializer = ChangePasswordSerializer(data= request.data)
    if serializer.is_valid():
        password = request.data['old_password']
        print(password)
        if user.check_password(password):
            print('yes')
            user.set_password(request.data['new_password'])
            user.save()
            return Response({"messgae":"password changed successfully"})
        else:
            return Response({"message":"old password not correct"})
    else:
        return Response({"message":"new password not equal password confirmation"})

### endpoint for resgisteration ###
class SignUpView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(    
            {"message": "The verification code has been sent to your email."},
            status=status.HTTP_201_CREATED
        )

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

### endpoint to log in via google account ###
class GoogleRedirectURIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Extract the authorization code from the request URL
        code = request.GET.get('code')
        print(f"Authorization code: {code}")
        data = {}
        token = None
        
        if code:
            print("Received authorization code")
            # Prepare the request parameters to exchange the authorization code for an access token
            token_endpoint = 'https://oauth2.googleapis.com/token'
            token_params = {
                'code': code,
                'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                # 'redirect_uri': 'https://abdulrahman.onrender.com/accounts/google/login/callback/',  # Must match the callback URL configured in your Google API credentials
                'redirect_uri': 'http://127.0.0.1:8000/accounts/google/login/callback/',  # Must match the callback URL configured in your Google API credentials
                'grant_type': 'authorization_code',
            }
            
            # Make a POST request to exchange the authorization code for an access token
            response = requests.post(token_endpoint, data=token_params)
            print('POST request sent to token endpoint')
            print(response.status_code)
            if not response.status_code == 200:
                print(response.status_code)
                print("##################################")
                print(response)
                print(code)
                return Response({"message": "Failed to exchange authorization code for access token."})
            else:
                access_token = response.json().get('access_token')
                print("status code 200")
                if not access_token:
                    return Response({"message": "Failed to receive access token."})
            
                print(f'Received access token:{access_token}')
                
                # Make a request to fetch the user's profile information
                profile_endpoint = 'https://www.googleapis.com/oauth2/v1/userinfo'
                headers = {'Authorization': f'Bearer {access_token}'}
                profile_response = requests.get(profile_endpoint, headers=headers)
                
                if not profile_response.status_code == 200:
                    return Response({"message": "Failed to fetch user profile information."})
                print("Received profile information")
                data = {}
                profile_data = profile_response.json()
                
                # Extract user data from the profile
                email = profile_data["email"]
                print(email)
                first_name = profile_data["given_name"]
                print(first_name)
                last_name = profile_data.get("family_name", "")
                print(last_name)
                
                # Try to get an existing user by email, or create a new one
                # if user already exists ##
                try:
                    user = User.objects.get(email=email)
                    print('welcome')
                except User.DoesNotExist:
                    print('new')
                    user = User.objects.create(
                        email=email,
                        first_name=first_name,
                        last_name=last_name
                    )
                    user.username = f"{first_name}{user.id}"
                    user.save()
                
                
                # Generate tokens for the user
                refresh = RefreshToken.for_user(user)
                data['access'] = str(refresh.access_token)
                data['refresh'] = str(refresh)
                token_obj, created = Token.objects.get_or_create(user=user)
                token = token_obj.key
                data['token'] = token
                print(data['access'])
                print(data['refresh'])
                print(data['token'])
                # return Response({'message': 'Logged in successfully!', 'token': token})

                
                redirect_url = f'/accounts/token/{email}/'
                return redirect(redirect_url)

### token endpoint ###
@api_view(['GET'])
def tokengetterview(request , email):
    user = User.objects.get(email=email)
    token = Token.objects.get(user=user).key
    data = {"message":"loged in successfully!" , "token":token}
    return Response(data)


        
class GoogleLogIn(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # redirect_uri = 'https://abdulrahman.onrender.com/accounts/google/login/callback/'  # Update with your actual redirect URI
        redirect_uri = 'http://127.0.0.1:8000/accounts/google/login/callback/'  # Update with your actual redirect URI
        scope = 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email'
        client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY

        # Constructing the authentication URL with prompt=select_account
        redirect_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&scope={scope}&access_type=offline&redirect_uri={redirect_uri}&prompt=select_account"
        # redirect_url = "http://127.0.0.1:8000/accounts/googlesignup/"

        return redirect(redirect_url)    


### endpoint for forget password ###
class ForgetPassword(generics.CreateAPIView):
    serializer_class = ForgetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            token = getattr(serializer, 'token' , None)
            print(f'the token: {token}')
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
            print('token2'+token)
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
            print(f'the tokeny:{token}')
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
    email = data['email']
    print(email)
    password = data['password']
    try:
        user = User.objects.get(email=email)
        username = user.username
        print(username)
        user2 = authenticate(username=username , password=password)
        if user2:
            token = Token.objects.get(user=user)
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

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from UserApp.models import Profile
from UserApp.api.serializers import UserSerializer, ProfileSerializer


    
@api_view(['POST',])
def RegistrationView(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)  
        data = {}

        if serializer.is_valid():
            account = serializer.save()
            data['response'] = "successfully registered"
            data['username'] = account.username
            data['email'] = account.email
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            token = Token.objects.get(user=account).key
            data['token'] = token
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
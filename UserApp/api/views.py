from rest_framework.decorators import api_view
from rest_framework.response import Response
from UserApp import models
from UserApp.api.serializers import UserSerializer
from rest_framework.authtoken.models import Token
    
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
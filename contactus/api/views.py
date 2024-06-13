from django.shortcuts import render
from .serializers import ContactUsSerializer
from contactus.models import ContactMessage
from rest_framework import generics
from .permissions import IsAdminUser

## endpoint create new message for contact us ##
class PostMessage(generics.CreateAPIView):
    queryset = ContactMessage
    serializer_class = ContactUsSerializer

## endpoint list all contact us messages for admin ##
class ListMessages(generics.ListAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactUsSerializer
    permission_classes = [IsAdminUser]



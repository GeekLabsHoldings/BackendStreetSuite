from .serializers import ChangLogSerializer , MessageSerializer
from .permissions import IsAdminUser
from change_log.models import ChangeLog , Message
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status


class PostChangeLog(generics.CreateAPIView):
    queryset = ChangeLog.objects.all()
    serializer_class = ChangLogSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            "message": "New change log sent successfully!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)

## endpoint list all contact us messages for admin ##
class ListChangeLog(generics.ListAPIView):
    queryset = ChangeLog.objects.all()
    serializer_class = ChangLogSerializer

class PostMessage(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            "message": "Message sent successfully!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)

## endpoint list all contact us messages for admin ##
class ListMessage(generics.ListAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAdminUser]


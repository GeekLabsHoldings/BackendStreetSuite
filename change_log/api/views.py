from .serializers import ChangLogSerializer , MessageSerializer
from .permissions import IsAdminUser
from change_log.models import ChangeLog , Message
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

class PostChangeLog(generics.CreateAPIView):
    serializer_class = ChangLogSerializer
    # permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "New change log sent successfully!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

class PostMessage(generics.CreateAPIView):
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Message sent successfully!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

## endpoint list all contact us messages for admin ##
class ListChangeLog(generics.ListAPIView):
    queryset = ChangeLog.objects.all().order_by("-date")
    serializer_class = ChangLogSerializer

## endpoint list all contact us messages for admin ##
class ListMessage(generics.ListAPIView):
    queryset = Message.objects.all().order_by("-date")
    serializer_class = MessageSerializer
    # permission_classes = [IsAdminUser]


from .serializers import ChangLogSerializer
from .permissions import IsAdminUser
from change_log.models import ChangeLog
from rest_framework import generics


class PostChangeLog(generics.CreateAPIView):
    queryset = ChangeLog
    serializer_class = ChangLogSerializer

## endpoint list all contact us messages for admin ##
class ListChangeLog(generics.ListAPIView):
    queryset = ChangeLog.objects.all()
    serializer_class = ChangLogSerializer
    permission_classes = [IsAdminUser]


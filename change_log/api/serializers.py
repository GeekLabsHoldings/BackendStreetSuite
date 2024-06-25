from rest_framework import serializers
from change_log.models import ChangeLog

class ChangLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeLog
        fields = ['message' , 'date']
        


from rest_framework import serializers
from change_log.models import ChangeLog , Message

class ChangLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeLog
        fields = ['message' , 'date']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['text_message' , 'date']
        


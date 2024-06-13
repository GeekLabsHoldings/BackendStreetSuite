from rest_framework import serializers
from contactus.models import ContactMessage

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        exclude = ['id']


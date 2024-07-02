from rest_framework import serializers
from reviewapp.models import Review
from django.contrib.auth.models import User

class ReviewSerializer(serializers.ModelSerializer):
    posted_on = serializers.DateTimeField(required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)    
    
    class Meta:
        model = Review
        fields = "__all__"

    def create(self, validated_data):
        validated_data["show"] = True
        review = Review.objects.create(**validated_data)
        return review
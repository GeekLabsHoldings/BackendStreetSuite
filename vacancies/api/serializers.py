from rest_framework import serializers
from vacancies.models import Vacancy , Application

### serializer class for vacancy ### 
class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy 
        fields = "__all__"

## serializer class for application ### 
class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application 
        fields = "__all__"
    
    def create(self, validated_data):
        slug = self.context.get("slug")
        return Vacancy.objects.create(vacancy__slug = slug , first_name=validated_data["first_name"],
                              last_name = validated_data["last_name"], email= validated_data["email"],
                              portofolio_link = validated_data["portofolio_link"],git_hub_link=validated_data["git_hub_link"],
                              cv= validated_data["cv"])
        # return super().create(vacancy__slug=slug, first_name= validated_data)

## serializer class for application list ### 
class ApplicationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application 
        exclude = ['id' , 'vacancy']

## serializer for list vacancies only ##
class VacanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        exclude = ['id' ,'user' ]

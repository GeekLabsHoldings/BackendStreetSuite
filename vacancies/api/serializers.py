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

## serializer class for application list ### 
class ApplicationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application 
        exclude = ['id' , 'vacancy']

## serializer for list vacancies only ##
class VacanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        exclude = ['id' ,'user' ,'slug']

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
    
from rest_framework.response import Response 
from rest_framework import status , generics 
from .serializers import VacancySerializer , ApplicationSerializer 
from vacancies.models import Vacancy ,Application
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUser 

## view to post new vacancy ##
class PostCareer(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = VacancySerializer

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data["user"] = request.user.id
        serializer = VacancySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
## view to apply on vacancy ##
class ApplyVacancy(generics.CreateAPIView):

    def post(self, request, slug, *args, **kwargs):
        data = request.data.copy()
        vacancy = Vacancy.objects.get(slug=slug).pk
        data['vacancy'] = vacancy
        serializer = ApplicationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

### list applications for specefic vscancy##
class VacancyApplications(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        # Get the slug from the URL parameters
        slug = self.kwargs[self.lookup_field]
        # Filter applications based on the vacancy slug
        return Application.objects.filter(vacancy__slug=slug)

## endpoint to list vacancies for all users ##
class List_Vacancies(generics.ListAPIView):
    queryset = Vacancy.objects.all().order_by("-id")
    serializer_class = VacancySerializer
     
## endpoint to Retrieve Update and delete a vacancy for admin ##
class VacancyEdit(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'slug'

## endpoint to Retrieve Update and delete a vacancy for admin ##
class VacancyDetail(generics.RetrieveAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    lookup_field = 'slug'

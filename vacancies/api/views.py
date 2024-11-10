from rest_framework.response import Response 
from rest_framework import status , generics 
from .serializers import   VacancySerializer , ApplicationSerializer , VacanyListSerializer , ApplicationListSerializer 
from rest_framework.decorators import api_view  , permission_classes
from vacancies.models import Vacancy ,Application
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .permissions import IsAdminUser , IsAdminPosted


## view to post new vacancy ##
class PostCareer(generics.CreateAPIView):
    # permission_classes = [IsAdminUser]
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
    serializer_class = ApplicationSerializer

    def post(self, request, slug , *args, **kwargs):
        data = request.data.copy()
        # data['vacancy'] = Vacancy.objects.get(slug=slug).pk
        serializer = ApplicationSerializer(data=data,context={'slug': slug})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)


# @api_view(['POST'])
# @csrf_exempt
# # @authentication_classes([TokenAuthentication])
# def apply_vacancy(request , vacancy_slug):
#     # check if an vacancy id is exist or not ## 
#     if not Vacancy.objects.filter(slug= vacancy_slug).exists():
#         return Response({'error': 'there is no vacancy with that id'} , status= status.HTTP_400_BAD_REQUEST) 
#     # add vacancy id in data request to the application  ##
#     request.data['vacancy'] = Vacancy.objects.get(slug= vacancy_slug).id 
#     serializer = ApplicationSerializer(data= request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data,status=status.HTTP_201_CREATED)
#     else :
#         return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

### list applications for specefic vscancy##
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
def list_applications(request , vacancy_slug):
    ## check if vacancy is exists ##
    if not Vacancy.objects.filter(slug= vacancy_slug).exists():
        return Response({'error': 'there is no vacancy with that id'} , status= status.HTTP_400_BAD_REQUEST) 
    ## get all applications for the vacancy needed ##
    needed_vacancy = Vacancy.objects.get(slug= vacancy_slug)
    # vacancy_id = needed_vacancy.id
    ### check if request user is the same user who post the vacancy ## 
    if request.user == needed_vacancy.user:
        ## get all applications for the vacancy needed ##
        applications = Application.objects.filter(vacancy = needed_vacancy.id)
        srializer = ApplicationListSerializer(applications , many= True)
        return Response(srializer.data , status= status.HTTP_200_OK)
    return Response({'error':'you are not valid to see that applications!'})

## endpoint to list vacancies for all users ##
class List_Vacancies(generics.ListAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacanyListSerializer

    
## endpoint to Retrieve Update and delete a vacancy for admin ##
class VacancyDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacanyListSerializer
    permission_classes = [IsAdminPosted]
    lookup_field = 'slug'

## endpoint to Retrieve Update and delete a vacancy for admin ##
class VacancyDetailUser(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacanyListSerializer
    permission_classes = [IsAdminPosted]
    lookup_field = 'slug'

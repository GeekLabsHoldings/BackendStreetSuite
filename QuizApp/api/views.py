from rest_framework import generics, filters
from rest_framework.views import APIView
from QuizApp.models import Question, SubCategory, Category, UserEmail
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (SubCategoryListSerializer, QuestionsSerializer, CategorySerializer ,
                           SubCategoryDetailSerializer, SubCategoryCreateSerializer, UserEmailSerializer)



class LatestSubCategoriesView(generics.ListAPIView):
    serializer_class = SubCategoryListSerializer
    def get_queryset(self):
        return SubCategory.objects.all().order_by('-date_created')[:4]

class CategoryView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['text']
    search_fields = ['quizzes__title']

class SubCategoryList(generics.ListAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategoryListSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['title']

class SubCatergoryCreateView(generics.CreateAPIView):
   
    serializer_class = SubCategoryCreateSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 

class SubCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'pk'
    serializer_class = SubCategoryDetailSerializer
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return SubCategory.objects.filter(pk=pk) 
    
    def get_serializer_context(self):
        return {'request': self.request}
    

class Questions(APIView):
    def get(self, request, format=None, **kwargs):
        subcategory_id= self.kwargs.get('subcategory_id')
        random_questions = Question.objects.filter(subcategory_id=subcategory_id).order_by('?')[:5]
        serializer = QuestionsSerializer(random_questions, many=True)
        return Response(serializer.data)

class SendResult(APIView):

    def post(self, request, **kwargs):
        if request.user.is_authenticated:
            email = request.user.email
        else:
            email = request.data.get('email')
        result = float(request.data.get('result'))
        pk = request.data.get('quiz_id')
        instance = SubCategory.objects.get(id=pk)
        instance.total_entries += 1
        if result > (instance.result) /2:
            instance.total_passed += 1
            
        instance.avg_passed = (instance.total_passed / instance.total_entries)*100
        instance.save()

        user_email, created = UserEmail.objects.get_or_create(email=email, subcategory=instance)
        user_email.result = user_email.result + result
        user_email.save()    

        if not instance.users.filter(id=user_email.id).exists():
            instance.users.add(user_email)

        return Response({ 'response' :f"GREAT!, your score is {user_email.result}",
                              'result' : user_email.result})
       
 
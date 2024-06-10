from rest_framework import generics, filters
from .serializers import QuizListSerializer, QuestionsSerializer, CategorySerializer , QuizDetailSerializer
from rest_framework.views import APIView
from QuizApp.models import Question, Quizzes, Category 
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


class CategoryView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

class QuizList(generics.ListAPIView):
    queryset = Quizzes.objects.all()
    serializer_class = QuizListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['categories']
    search_fields = ['title']


class QuizDetailView(APIView):
    lookup_field = 'pk'
    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        quiz = Quizzes.objects.get(pk=pk)
        serializer = QuizDetailSerializer(quiz, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        pass

class Questions(APIView):
    def get(self, request, format=None, **kwargs):
        quiz_id = self.kwargs.get('quiz_id')
        questions = Question.objects.filter(quiz_id=quiz_id)
        serializer = QuestionsSerializer(questions, many=True)
        return Response(serializer.data)
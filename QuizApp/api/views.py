from rest_framework import generics, filters
from .serializers import QuizSerializer, RandomQuestionSerializer, CategorySerializer
from rest_framework.views import APIView
from QuizApp.models import Question, Quizzes, Category 
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


class QuizList(generics.ListAPIView):
    queryset = Quizzes.objects.all()
    serializer_class = QuizSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['categories']
    search_fields = ['title']

class CategoryView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

class QuizDetail(APIView):
    pass
class RandomQuestion(APIView):
    def get(self, request, format=None, **kwargs):
        question = Question.objects.filter(quiz__title=kwargs['topic']).order_by('?')[:1]
        serlializer = RandomQuestionSerializer(question, many=True)
        return Response(serlializer.data)
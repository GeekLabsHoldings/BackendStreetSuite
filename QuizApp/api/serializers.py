from rest_framework import serializers
from QuizApp.models import Quizzes, Question, Answer, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    
    class Meta:
        model = Quizzes
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = [
            'answer_text',
            'is_right',
        ]
        
class RandomQuestionSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(many=True)
    class Meta:
        model = Question
        fields = [
            'title',
            'answer',
        ]
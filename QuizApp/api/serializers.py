from rest_framework import serializers
from QuizApp.models import Quizzes, Question, Answer, Category
from rest_framework.reverse import reverse

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['id','text']

class QuizListSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    quiz_detail = serializers.HyperlinkedIdentityField(
        view_name='quiz-detail',
        lookup_field='pk',
        read_only=True
    )
    class Meta:
        model = Quizzes
        fields = ['categories', 'id', 'title', 'date_created', 'label', 'enrollers', 'likes', 'achievement', 'quiz_detail']

class QuizDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    questions_url = serializers.SerializerMethodField()
    class Meta:
        model = Quizzes
        fields = '__all__'
        
    def get_questions_url(self, obj):
        request = self.context.get('request')
        return reverse('questions', kwargs={'quiz_id': obj.pk}, request=request)

    
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = [
            'answer_text',
            'is_right',
        ]
        
class QuestionsSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(many=True)
    class Meta:
        model = Question
        fields = [
            'title',
            'answer',
        ]
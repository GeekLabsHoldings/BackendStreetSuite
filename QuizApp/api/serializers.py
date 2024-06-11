from rest_framework import serializers
from QuizApp.models import Quizzes, Question, Answer, Category, UserEmail
from rest_framework.reverse import reverse

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','text']
        ref_name = 'QuizAppCategory'

class QuizListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quizzes
        fields = ['categories', 'id', 'title', 'date_created', 'label', 'enrollers', 'likes', 'achievement', 'quiz_detail', 'image_url']
   
    image_url = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True)
    quiz_detail = serializers.HyperlinkedIdentityField(
        view_name='quiz-detail',
        lookup_field='pk',
        read_only=True
    )
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        else:
            return None

class QuizCreateSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True)
    class Meta:
        model = Quizzes
        fields = ['categories', 'title', 'label', 'description', 'duration', 'score', 'image_url']

    def create(self, validated_data):
        categories_data = validated_data.pop('categories')
        quiz = Quizzes.objects.create( **validated_data)    
        
        for category_data in categories_data:
            category, created = Category.objects.get_or_create(text=category_data['text'])
            quiz.categories.add(category)
        return quiz
    
    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', None)
        if categories_data:
            instance.categories.clear()
            for category_data in categories_data:
                category = Category.objects.get_or_create(text=category_data['text'])
                instance.categories.add(category)
        return super().update(instance, validated_data)

        
    def to_representation(self, instance):
        from UserApp.api.serializers import UserSerializer  
        ret = super().to_representation(instance)
        ret['author'] = UserSerializer(instance.author).data 
        return ret
    
class QuizDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True)
    questions_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Quizzes
        fields = '__all__'

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        else:
            return None
    def get_author(self, obj):
      return {
          'first_name': obj.author.first_name,
          'last_name': obj.author.last_name
      }
    def create(self, validated_data):
        categories_data = validated_data.pop('categories')
        quiz = Quizzes.objects.create( **validated_data)    
        
        for category_data in categories_data:
            category, created = Category.objects.get_or_create(text=category_data['text'])
            quiz.categories.add(category)
        return quiz
    
    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', None)
        if categories_data:
            instance.categories.clear()
            for category_data in categories_data:
                category = Category.objects.get_or_create(text=category_data['text'])
                instance.categories.add(category)
        return super().update(instance, validated_data)

        
    def to_representation(self, instance):
        from UserApp.api.serializers import UserSerializer  
        ret = super().to_representation(instance)
        ret['author'] = UserSerializer(instance.author).data 
        return ret
    
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
class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEmail
        fields = ['email', 'result']
    
from rest_framework import serializers
from QuizApp.models import SubCategory, Question, Answer, Category, UserEmail
from rest_framework.reverse import reverse


class SubCategoryListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    quiz_detail = serializers.HyperlinkedIdentityField(
        view_name='quiz-detail',
        lookup_field='pk',
        read_only=True
    )
    class Meta:
        model = SubCategory
        fields = [ 'id', 'title', 'date_created', 'label', 'quiz_detail', 'image_url']
   
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        else:
            return None
class CategorySerializer(serializers.ModelSerializer):
    quizzes = SubCategoryListSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id','text', 'quizzes']
        ref_name = 'QuizAppCategory'
    def to_representation(self, instance):
        representation = super().to_representation(instance)    
        if instance.text == "latest":
                latest_subcategories = SubCategory.objects.all().order_by('-date_created')[:10]
                subcategory_serializer = SubCategoryListSerializer(latest_subcategories, many=True, context=self.context)
                representation['quizzes'] = subcategory_serializer.data
        return representation




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
    


class SubCategoryCreateSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    questions = QuestionsSerializer(many=True)
    answer = AnswerSerializer(many=True)
    class Meta:
        model = SubCategory
        fields = ['category', 'title', 'label', 'description', 'duration', 'score', 'image_url', 'questions', 'answer']

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        questions_data = validated_data.pop('questions', [])

        
        category, created = Category.objects.get_or_create(text=category_data['text'])
        subcategory = SubCategory.objects.create(category=category, **validated_data)

        for question_data in questions_data:
            answers_data = question_data.pop('answer', [])
            question = Question.objects.create(subcategory=subcategory, **question_data)
            for answer_data in answers_data:
                Answer.objects.create(question=question, **answer_data)

        return subcategory

    def update(self, instance, validated_data):
        category_data = validated_data.pop('category', None)
        if category_data:
            category, created = Category.objects.get_or_create(text=category_data['text'])
            instance.category = category
        
        questions_data = validated_data.pop('questions', None)
        if questions_data:
            instance.questions.all().delete()
            for question_data in questions_data:
                answers_data = question_data.pop('answer', [])
                question = Question.objects.create(subcategory=instance, **question_data)
                for answer_data in answers_data:
                    Answer.objects.create(question=question, **answer_data)
        
        return super().update(instance, validated_data)
        
    def to_representation(self, instance):
        from UserApp.api.serializers import UserSerializer  
        ret = super().to_representation(instance)
        ret['author'] = UserSerializer(instance.author).data 
        return ret
    
class SubCategoryDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    questions_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = SubCategory
        exclude =['questions_counter']

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
    def get_category(self, obj):
        return {
            'text': obj.category.text
        }

    def update(self, instance, validated_data):
        category_data = validated_data.get('category')
        if category_data:
            instance.category.text = category_data.get('text', instance.category.text)
            instance.category.save()
        return super().update(instance, validated_data)
    
    def get_questions_url(self, obj):
        request = self.context.get('request')
        return reverse('questions', kwargs={'subcategory_id': obj.pk}, request=request)

    
        
class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEmail
        fields = ['email', 'result']
    
from rest_framework import serializers
from Courses.models import Course, Articles, Module, Assessment , Category , Subscribed_courses , Questions , Answers

## serializer of category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title']

# serializer of Courses
class CourseSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    author_field = serializers.SerializerMethodField()
    
    category = serializers.SerializerMethodField()
    class Meta:
        model = Course 
        fields = ['id','title','author_field',
                  'category','image_url','likes_number',
                  'subscriber_number','duration','users_completed',
                    'published_date','slug', 'level',
                    'label']

    # Modify the get_is_applied method to check if the course is applied by the user
    def get_category(self, obj):
        return obj.category.title

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url    
        else:
            return None
        
    def get_author_field(self, obj):
        return  obj.author.first_name + ' ' + obj.author.last_name
    
#serializer of Courses details 
class CourseDetailsSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    author_field = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()
    modules_number = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ['id','author_field' ,'category','image_url',
                  'title','likes_number','description',
                  'subscriber_number','duration','users_completed',
                   'is_applied', 'modules', 'modules_number', 
                  'slug','published_date', 
                  'level', 'label']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url    
        else:
            return None
        
    def get_is_applied(self, obj):
        user = self.context.get('request').user
        return Subscribed_courses.objects.filter(user=user, course=obj).exists()
    
    def get_modules(self, obj):
        if obj.modules:
            modules = obj.modules.values_list('title',flat=True)
            return modules
        else:
            return None
    
    def get_modules_number(self, obj):
        if obj.modules:
            modules_number = obj.modules.count()
            return modules_number
        else:
            return None

    def get_author_field(self, obj):
        return obj.author.first_name + ' ' +  obj.author.last_name 

    def get_category(self, obj):
        return obj.category.title
    
# serializer for articles 
class ArticleSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Articles
        fields = ['title','article','image_url']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url    
        else:
            return None

# serializer for modules 
class ModuleSerializer(serializers.ModelSerializer):
    article_modules= ArticleSerializer(many=True, read_only=True)
    class Meta:
        model = Module
        fields = ['id','title', 'description', 'article_modules','slug']

# serializer for subscribed courses
class AppliedCourseLisSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    class Meta:
        model = Subscribed_courses
        fields = ['course','completed_modules','start_date' , 'assessment_score']

class Applied_course_Detail_Srializer(serializers.ModelSerializer):                   
    course = CourseDetailsSerializer()
    class Meta:
        model = Subscribed_courses
        fields = ['course','completed_modules','start_date' , 'assessment_score']

# serializer for answers 
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Answers
        exclude = ['question','is_correct']

# serializer for answers in correction process
class AnswerSubmistionSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Answers
        fields = ['id','is_correct']

# serializer for question process
class QuestionsSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, source='assessment_answers' , read_only=True )
    class Meta:
        model =  Questions
        fields = ['text', 'answers']
    
# serializer for Assessment 
class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ['id','description','instructions']

# serializer for answersubmet
class SubmitAnswersSerializer(serializers.Serializer):
    answers = serializers.ListField()
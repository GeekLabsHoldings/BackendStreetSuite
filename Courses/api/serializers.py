from rest_framework import serializers
from Courses.models import Course, Articles, Module, Assessment , Category , Subscribed_courses , Questions , Answers

## serializer of category ## 
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title']

## serializer of Courses ##
class CourseSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    author_field = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ['id','author_field' ,'category','image_url','title','likes_number','description','subscriber_number','duration','users_completed' , 'number_of_modules']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url    
        else:
            return None

    def get_author_field(self, obj):
        return {
            'author_name': obj.auther.first_name + obj.auther.last_name
        }

## serializer for subscribed courses ##
class Apply_course_Srializer(serializers.ModelSerializer):
    # course = CourseSerializer()
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    class Meta:
        model = Subscribed_courses
        fields = ['user','course','completed_modules','start_date' , 'assessment_score']

## serializer for modules to get titles ##
class ModuleTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['title']

## class to retrieve course details shown for user that apply it (subscribe on it)##
class CourseDetailsSerializer(serializers.ModelSerializer):
    modules = ModuleTitleSerializer(many=True)
    image_url = serializers.SerializerMethodField()
    author_field = serializers.SerializerMethodField()
    category = CategorySerializer()
    class Meta:
        model = Course
        fields = ['title','author_field','category','image_url','likes_number','description','subscriber_number','duration','users_completed','modules']
        # read_only_fields = ('')
        # depth = 2

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url    
        else:
            return None
        
    def get_author_field(self, obj):
        return {
            'author_name': obj.auther.first_name + ' ' + obj.auther.last_name
        } 


## serializer for articles ##
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

## serializer for modules ##
class ModuleSerializer(serializers.ModelSerializer):
    article_modules= ArticleSerializer(many=True, read_only=True)
    class Meta:
        model = Module
        fields = ['title', 'description', 'article_modules']

    

"""
{
    "id": 1,
    "text": "What is the capital of France?",
    "answers_lists": [
        {"text": "Paris", "is_correct": true},
        {"text": "London", "is_correct": false},
        {"text": "Berlin", "is_correct": false}
    ],
    "assessment_id": 2
}"""



    # def create(self, validated_data):
    #     # Extracting the answers data from validated data
    #     answers_data = validated_data.pop('answers_list',[])
    #     print(answers_data)
    #     # assessment_id = validated_data.pop('assessment_id') ## to extract answers from validate post data ##
    #     # assessment , created = Assessment.objects.get_or_create(id=assessment_id)
    #     # Creating the Question instance, with the associated Assessment
    #     question = Question.objects.create(**validated_data , assessment=Assessment.objects.first())

    #     # Creating the Answer instances associated with the Question
    #     for answer_data in answers_data:
    #         Answer.objects.create(question=question, **answer_data)

    #     return question

    # ## method to create a new question with its answers ##
    # def create(self, validated_data):
    #     answers = validated_data.pop('answers_lists') ## to extract answers from validate post data ##
    #     print(answers)
        # assessment_id = validated_data.pop('assessment_id') ## to extract answers from validate post data ##
        # assessment , created = Assessment.objects.get_or_create(id=assessment_id)
    #     ## create object for question ##
    #     question = Question.objects.create(**validated_data , assessment=Assessment.objects.first())
    #     ## looping on posted answers list to create objects for each answer ##
    #     for answer in answers:
    #         Answer.objects.create(**answer , question=question)
    #     return question

    ## method to update values for question and/or answers ##
    # def update(self, instance, validated_data):
    #     ## extract answers data from post data ##
    #     ansers = validated_data.pop('answers_lists')
    #     instance.text = validated_data.get('text' , instance.text) ## update question 
    #     # for 


'''
[ { "question_id": 1,"answer_text": "Answer 1"},{"question_id": 2,"answer_text": "Answer 2"}]
'''

################## New Serialization ###################
##### serializer for answers ######
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Answers
        exclude = ['question','is_correct']

##### serializer for answers in correction process ######
class AnswerSubmistionSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Answers
        fields = ['id','is_correct']

##### serializer for question process ######
class QuestionsSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, source='course_answers' , read_only=True )
    class Meta:
        model =  Questions
        fields = ['text', 'answers']

    # # create method ##
    # def create(self, validated_data):
    #     print(validated_data)
    #     # course_slug = validated_data.pop('course_slug')
    #     # print(course_slug)
    #     answers = validated_data.pop("answers")
    #     question = Questions.objects.create(**validated_data,course=Course.objects.get(id=4))
    #     for answer_data in answers:
    #         answer = Answers.objects.create(question=question, **answer_data)
    #     return question
    
## serializer for Assessment ##
class AssessmentSerializer(serializers.ModelSerializer):
    # questions = serializers.SerializerMethodField()
    class Meta:
        model = Assessment
        fields = ['id','description','instructions']

## serializer for answersubmet ##
class SubmitAnswersSerializer(serializers.Serializer):
    answers = serializers.ListField()
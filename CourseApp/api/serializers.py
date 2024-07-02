from rest_framework import serializers
from CourseApp.models import Course, Section, Module, Answer, Question, Assessment, AssessmentCompleted
from UserApp.api.serializers import UserSerializer
from django.db.models import F
import random


class CourseSerializer(serializers.ModelSerializer):
    user = UserSerializer(required = False)
    user_likes_course = serializers.SerializerMethodField(required = False)
    user_subscribed_course = serializers.SerializerMethodField(required = False)
    module_numbers = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "image", "title", "description", "difficulty", "subscriber_number", "completed", "duration", "time_to_complete", "likes_number","user", 
                  "user_likes_course", "user_subscribed_course", "category", "module_numbers"]
    
    def get_module_numbers(self, obj):
        return obj.modules.count()
    
    def get_user_likes_course(self, obj):
        # Check if the current user (from context) has liked this course
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def get_user_subscribed_course(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.subscribed.filter(id=request.user.id).exists()
        return False
    
    def create(self, validated_data):
        course = Course.objects.create(**validated_data)
        return course

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    
    def delete(self, instance):
        instance.delete()

# class Coursesubscribeserializer(CourseSerializer):
#     def update(self, instance, validated_data):



class SectionSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ['id', 'title', 'article', 'image', 'is_completed',]

    def get_is_completed(self, obj):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            return obj.completed.filter(id=request.user.id).exists()
        return False


class ModuleSerializer(serializers.ModelSerializer):
    section_set = SectionSerializer(many=True)
    completed = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'section_set', "course", "completed"]
    
    def get_completed(self, obj):
        user_id = self.context['request'].user.id
        module_id = obj.id
        course = obj.course
        
        module_count = course.modules.count()
        module_completed_count = AssessmentCompleted.objects.filter(user_id=user_id, module_id=module_id).count()
        print(module_completed_count, module_count)

        return (module_completed_count / module_count) * 100

    def create(self, validated_data):
        sections_data = validated_data.pop('section_set', [])
        module = Module.objects.create(**validated_data)
        
        for section_data in sections_data:
            Section.objects.create(module=module, **section_data)

        return module
    
    def update(self, instance, validated_data):
        sections_data = validated_data.pop('section_set', [])
        instance = super().update(instance, validated_data)

        # Update related sections
        for section_data in sections_data:
            section, _ = Section.objects.get_or_create(module=instance, title=section_data['title'])

            for key, value in section_data.items():
                if hasattr(section, key):
                    setattr(section, key, value)

            section.save()

        return instance
    def delete(self, instance):
        instance.delete() 

class AnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["text", "is_correct", ]

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswersSerializer(many=True)
    
    class Meta:
        model = Question
        fields = [ "text", "answers"]

    @classmethod
    def get_random_questions(cls, assessment_id):
        random_questions = Question.objects.filter(assessment_id=assessment_id).order_by('?')[:5]
        return random_questions

    @classmethod
    def get_random_question_data(cls):
        random_questions = cls.get_random_questions()
        return cls(random_questions, many=True).data


class AssmentsSerializer(serializers.ModelSerializer):
    assment_questions =  serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Assessment
        fields = ["description", "instructions","questions", "module", "is_completed", "assment_questions"]

    def get_is_completed(self, obj):
        request = self.context.get("request")
        user_id = request.user.id if request and request.user.is_authenticated else None

        if user_id and obj.id:
            assessment_completed = AssessmentCompleted.objects.filter(user_id=user_id, assessment_id=obj.id).first()
            if assessment_completed:
                return {
                    "score": assessment_completed.score,
                }
            else:
                return {
                    "is_completed": False,
                }
        return False
    
    def get_assment_questions(self, obj):
        assessment_id = obj.id
        random_questions = QuestionSerializer.get_random_questions(assessment_id)
        return QuestionSerializer(random_questions, many=True).data
    
    def create(self, validated_data):
        print(validated_data)
        question_set = validated_data.pop("questions", [])

        assessment = Assessment.objects.create(**validated_data)

        print(question_set)
        for question_data in question_set:
            answers = question_data.pop("answers")

            question = Question.objects.create(assessment=assessment, **question_data)

            for answer_data in answers:
                Answer.objects.create(question=question,**answer_data)

        return assessment
    
    def update(self, instance, validated_data):
        for field in ["description", "instructions", "score"]:
            setattr(instance, field, validated_data.get(field, getattr(instance, field)))

        for question_data in validated_data.get("questions", []):
            question_id = question_data.get("id")
            if question_id:
                question = Question.objects.get(pk=question_id)
                question.text = question_data.get("text", question.text)
                question.save()

                for answer_data in question_data.get("answers", []):
                    answer_id = answer_data.get("id")
                    if answer_id:
                        answer = Answer.objects.get(pk=answer_id)
                        answer.text = answer_data.get("text", answer.text)
                        answer.save()

        instance.save()
        return instance
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("questions")

        return data
    def delete(self, instance):
        instance.delete() 

class AssessmentCompletedSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= AssessmentCompleted
        fields = ["assessment", "score"]

    def create(self, validated_data):
        user = self.context['request'].user
        assessment = validated_data["assessment"]
       
            
        assessment_completed = AssessmentCompleted.objects.create(**validated_data)
        
        module = assessment_completed.assessment.module
        assessment_completed.module = module
        assessment_completed.save()

        course = assessment_completed.module.course


        module_count = course.modules.count()
        modules_completed = AssessmentCompleted.objects.filter(user=user, module=module).count()

        course.subscribed.add(user)
        course.subscribers += 1

        if modules_completed == module_count:
            course.users_completed.add(user)
            course.completed += 1

        course.save()



        return assessment_completed 

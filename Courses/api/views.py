from rest_framework.decorators import api_view 
from rest_framework.generics import ListAPIView, RetrieveAPIView  , CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from Courses.models import Course, Module, Assessment , Subscribed_courses   , Category , Answers, Questions
from Courses.api.serializers import (CourseSerializer , Apply_course_Srializer , CourseDetailsSerializer , AnswerSerializer ,AnswerSubmistionSerializer , QuestionsSerializer
                                     , ModuleSerializer , AssessmentSerializer  , SubmitAnswersSerializer  )
from Payment.api.permissions import HasActiveSubscription  
from .pagination import CoursePagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from collections import OrderedDict
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode

class CoursesListView(ListAPIView):
    # permission_classes = [HasActiveSubscription]
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    pagination_class = CoursePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title']

## endpoint to apply on any course ##
@api_view(['POST'])
def apply_course(request,slug):
    course = Course.objects.get(slug=slug)
    user = request.user
    try:
        application = Subscribed_courses.objects.get(user=user.pk , course=course.pk)
        return Response({"message":"you applied that course before"})
    except:
        try:
            data = request.data.copy()
            data['course'] = course.pk
            data['user'] = user.pk
            serializer = Apply_course_Srializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'you applied the course','data':serializer.data})
            else:
                return Response(serializer.errors)
        except:
            return Response({"message":"not found course!"})


## endpoint to show my only own courses ##
class ShowMyCourses(ListAPIView):
    # queryset = Subscribed_courses.objects.all()
    serializer_class = Apply_course_Srializer

    def get_queryset(self):
        data = Subscribed_courses.objects.filter(user=self.request.user)
        return data

## endpoint for course detail ##
class ShowCourseDetail(RetrieveAPIView):
    serializer_class = CourseDetailsSerializer
    queryset = Course.objects.all()
    lookup_field = 'slug'

## endpoint let user like the course ##
@api_view(['POST'])
def like_course(request ,slug):
    user = request.user
    course = Course.objects.get(slug=slug)
    if course.liked_users.filter(id=user.pk).exists():
        return Response({"message":f"you liked it before"})
    else:
        title = course.title
        course.likes_number += 1 
        course.liked_users.add(user)
        course.save()      
        return Response({"message":f"you liked {title}!"})

## endpoint to get all liked courses for request user ##
@api_view(['GET'])
def show_liked_course(request):
    ## query set to get courses liked for user ##
    course = Course.objects.filter(liked_users__id=request.user.pk)
    ## serialize courses ##
    serializer = CourseSerializer(course, many=True)
    return Response(serializer.data)

## endpoint to retrieve my own subscriped course ##
@api_view(['GET'])
def GetMyCourse(request , slug):
    try:
        mycourse = Subscribed_courses.objects.get(course__slug = slug ,  user = request.user )
        serialzer = Apply_course_Srializer(mycourse)
        return Response(serialzer.data)
    except:
        return Response({'message':'not subscribed course'})

## endpoint to list all modules for each course ##
class ListModulesCourse(ListAPIView):
    lookup_field='slug'
    serializer_class = ModuleSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        all_modules = Module.objects.filter(course__slug = slug)
        return all_modules


## complete module ##
@api_view(['post'])
def complete_module(request , course_slug , module_slug):
    ## increament the number of completed modules for user in the course ##
    subscribed_course = Subscribed_courses.objects.get(course__slug= course_slug , user = request.user ) 
    subscribed_course.completed_modules += 1 
    subscribed_course.save() 
    return Response({"message":f"module completed"})

## uncomplete module ##
@api_view(['post'])
def uncomplete_module(request , course_slug , module_slug):
    ## increament the number of completed modules for user in the course ##
    subscribed_course = Subscribed_courses.objects.get(course__slug= course_slug , user = request.user ) 
    subscribed_course.completed_modules -= 1 
    subscribed_course.save() 
    return Response({"message":f"module uncompleted"})

## open assessment in course finish ##
@api_view(['GET'])
def get_assessment(request, course_id):
    # get subscribed course for user##
    subscribed_course = Subscribed_courses.objects.get(course__id = course_id , user= request.user.pk)
    if subscribed_course.completed_modules != len(Module.objects.filter(course= Course.objects.get(id=course_id))):
        return Response({"message":"you didn't finished your modules yet"})
    # Fetch the assessment object
    assessment = Assessment.objects.get(course__id=course_id)
    # Serialize and return the response
    serializer = AssessmentSerializer(assessment)
    ## get question of assesments ##
    questions = Questions.objects.filter(course__id=course_id).order_by('?')[:3]
    questions_serializes = QuestionsSerializer(questions , many=True)
    ## responsed_data $$
    response_data = {
            'module': serializer.data,
            'questions': questions_serializes.data
        }
    return Response(response_data)

### structure for the request data for assessment results ###
'''
{
  "assessment_id":45,
  "answers": [
    { "question_id": 1, "answer_text": "gjiodndsnnk" },
    { "question_id": 2, "answer_text": "Answer 2" }
  ]
}
'''

## submit ansers ##
@api_view(['POST'])
def submetAnsers(request , assessment_id , course_slug):
    user = request.user
    answers = Answers.objects.filter(question__course__slug=course_slug)
    serialized_data = AnswerSubmistionSerializer(answers, many=True).data
    serializer_submeted_answer = SubmitAnswersSerializer(data=request.data)
    if serializer_submeted_answer.is_valid():
        score = 0
        for answer in serialized_data:
            if answer['is_correct'] == True and answer['id'] in serializer_submeted_answer.data['answers'] :
                score += 1
        score = (score/len(serializer_submeted_answer.data['answers']))*100
        ## add score to subscribed course attributes ###
        subscribed_course = Subscribed_courses.objects.get(course__slug=course_slug,user=user)
        subscribed_course.assessment_score = score
        subscribed_course.save()
    return Response({"score":score})

## enpoimt to restart course ##
@api_view(['POST'])
def restartcourse(request , course_slug):
    ## make all completed modules in Subscribed courses = 0 ##
    my_course = Subscribed_courses.objects.get(course__slug=course_slug , user = request.user)
    my_course.completed_modules = 0
    my_course.save()
    return Response({'message':'Restart Course completed!'})

## get most 2 likes number courses ##
class MostLikeCourses(ListAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        returned_data = Course.objects.order_by('-likes_number')[:2]
        return returned_data

## get most 2 compleated courses ##
class MostCompletedCourses(ListAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        returned_data = Course.objects.order_by('-users_completed')[:2]
        return returned_data

## recomendition endpoint ##
class RecomendationAPI(ListAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        # Get the categories of the courses the user is subscribed to
        user_courses = Subscribed_courses.objects.filter(user=self.request.user).order_by('-start_date')
        id_courses = []
        for course in user_courses:
            id_courses.append(course.course.pk)
        recomended_courses = Course.objects.filter(category = user_courses[0].course.category).order_by('-id').exclude(id__in=id_courses)[:2]
        return recomended_courses

## endpoint to create a new question with its answers ##
class CreateQuestion(CreateAPIView):
    queryset = Questions.objects.all()
    serializer_class = QuestionsSerializer

#### the structure of request data for create the question with the answers for course ###
"""
{
    "text": "What is the capital of France?",
    "answers": [
        {
            "text": "Berlin",
            "is_correct": false
        },
        {
            "text": "Madrid",
            "is_correct": false
        },
        {
            "text": "Paris",
            "is_correct": true
        }
    ]
}
"""
## endpoint to create quetions ##
@api_view(['POST'])
def createQuestion(request, course_slug):
    course = Course.objects.get(slug=course_slug)
    data = request.data.copy()
    ## create question ##
    question = Questions.objects.create(text=data['text'],course=course)
    question.save()
    for answer_data in data['answers']:
        answer = Answers.objects.create(question=question , text= answer_data['text'] , is_correct = answer_data['is_correct'])
        answer.save()
    return Response({'message':'new question created'})
#### list all answers ###
class ListAnswersss(ListAPIView):
    serializer_class = AnswerSubmistionSerializer
    queryset = Answers.objects.all()

#### list all questions ###
# class ListQuestion(ListAPIView):
#     serializer_class = QuestionsSerializer
#     queryset = Questions.objects.all()
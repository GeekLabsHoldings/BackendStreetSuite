from rest_framework.decorators import api_view , permission_classes
from django.db import transaction
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, RetrieveAPIView  , CreateAPIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from Courses.models import Course, Module, Assessment , Subscribed_courses, Answers, Questions
from Payment.api.permissions import HasActiveSubscription  
from .pagination import CoursePagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from .filters import CourseFilters
from Courses.api.serializers import (CourseSerializer, AppliedCourseListSerializer, CourseDetailsSerializer,
                                      AppliedCourseDetailSerializer, AnswerSubmistionSerializer, QuestionsSerializer,
                                        ModuleSerializer, AssessmentSerializer, SubmitAnswersSerializer)

class CoursesListView(ListAPIView):
    permission_classes = [HasActiveSubscription]
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    pagination_class = CoursePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = CourseFilters
    search_fields = ['title']

## endpoint to show my only own courses ##
class ShowMyCourses(ListAPIView):
    permission_classes = [HasActiveSubscription]
    serializer_class = AppliedCourseListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    def get_queryset(self):
        data = Subscribed_courses.objects.filter(user=self.request.user)
        return data


## endpoint for course detail ##
class ShowCourseDetail(RetrieveAPIView):
    permission_classes = [HasActiveSubscription]
    serializer_class = CourseDetailsSerializer
    queryset = Course.objects.all()
    lookup_field = 'slug'

## endpoint to retrieve my own subscribed course ##
class GetMyCourse(RetrieveAPIView):
    permission_classes = [HasActiveSubscription]
    serializer_class = AppliedCourseDetailSerializer
    # Use nested lookup for course slug
    lookup_field = 'course__slug'  
    # URL parameter name
    lookup_url_kwarg = 'course_slug'

    def get_queryset(self):
        # Return a queryset filtered by the authenticated user
        return Subscribed_courses.objects.filter(user=self.request.user)

    def handle_exception(self, exc):
        # Customize the error message if the subscription is not found
        if isinstance(exc, NotFound):
            return Response({'message': 'You did not subscribe to this course!'}, status=404)
        return super().handle_exception(exc)

## endpoint to apply on any course ##
@api_view(['POST'])
@permission_classes([HasActiveSubscription])
def apply_course(request,course_slug):
    course = Course.objects.get(slug=course_slug)
    user = request.user
    #check if the user is already subscribe to the course or create new subscription
    subscription , created = Subscribed_courses.objects.get_or_create(user=user, course=course)
    if created:
        return Response({"message": f"You have successfully subscribed to the course '{course.title}'."})
    else:
        return Response({"message": "You have already subscribed to this course."})


## endpoint let user like the course ##
@api_view(['POST'])
@permission_classes([HasActiveSubscription])
def like_course(request ,course_slug):
    user = request.user
    course = Course.objects.get(slug=course_slug)
    if course.liked_users.filter(id=user.pk).exists():
        return Response({"message":f"you have already liked this course before"})
    # using atomic transaction when doing multiple related operations are performed in sequence to
    # ensure that either both operations succeed or neither does
    with transaction.atomic():
        course.likes_number += 1 
        course.liked_users.add(user)
        course.save()      
    return Response({"message":f"liked {course.title}!"})

## endpoint to get all liked courses for the requested user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def show_liked_course(request):
    ## query set to get courses liked for user
    course = Course.objects.filter(liked_users = request.user)
    if course:
        ## serialize courses
        serializer = CourseSerializer(course, many=True,context={'request':request})
        return Response(serializer.data)
    return Response({"message":"no courses liked for you!"})


## endpoint to list all modules for each course ##
@api_view(['GET'])
def ListModulesCourse(request, course_slug):
    all_modules = Module.objects.filter(course__slug = course_slug)
    completed_modules_ids = Subscribed_courses.objects.get(course__slug = course_slug,user=request.user).completed_modules_ids
    module_serialized = ModuleSerializer(all_modules,many=True)
    return Response({"modules":module_serialized.data,"completed_modules_ids":completed_modules_ids})
    

## complete module ##
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_module(request , course_slug , module_id):
    ## increament the number of completed modules for user in the course ##
    subscribed_course = Subscribed_courses.objects.get(course__slug= course_slug , user = request.user ) 
    id = module_id
    
    if id not in subscribed_course.completed_modules_ids:
        subscribed_course.completed_modules += 1 
        list_ids = subscribed_course.completed_modules_ids
        list_ids.append(id)
        subscribed_course.save()
        total_modules = Module.objects.filter(course__slug=course_slug).count()
        if subscribed_course.completed_modules == total_modules:
            subscribed_course.status = 'Ready For Assessment'
            subscribed_course.save()
            return Response({"message":f"course completed, Ready for Assessment"})
        return Response({"message":f"module completed"})
    else :
        return Response({"message":"you already completed this module"})

## uncomplete module ##
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def uncomplete_module(request , course_slug , module_id):
    ## increment the number of completed modules for user in the course
    subscribed_course = Subscribed_courses.objects.get(course__slug= course_slug , user = request.user )
    id = module_id
    if id in subscribed_course.completed_modules_ids: 
        subscribed_course.completed_modules -= 1 
        list_ids = subscribed_course.completed_modules_ids
        list_ids.remove(id)
        if subscribed_course.status == 'completed' or subscribed_course.status == 'Ready For Assessment' :
            subscribed_course.status = 'in progress'
        subscribed_course.save() 
        return Response({"message":f"module uncompleted"})
    else:
        return Response({"message":"you didn't complete this module"})

## open assessment in course finish 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assessment(request, course_slug):
    # get subscribed course for user
    subscribed_course = Subscribed_courses.objects.get(course__slug = course_slug , user= request.user.pk)

    if subscribed_course.status == 'in progress':
        return Response({"message":"you didn't finished your modules yet"})
    # Fetch the assessment object
    assessment = Assessment.objects.get(course__slug=course_slug)
    # Serialize and return the response
    serializer = AssessmentSerializer(assessment)
    ## get question of assesments 
    questions = Questions.objects.filter(assessment=assessment).order_by('?')[:3]
    questions_serializes = QuestionsSerializer(questions , many=True)
    ## responsed_data 
    response_data = {
            'module': serializer.data,
            'questions': questions_serializes.data
        }
    return Response(response_data)

## submit ansers 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submitAnswers(request , assessment_id , course_slug):
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
        ## add score to subscribed course attributes 
        subscribed_course = Subscribed_courses.objects.get(course__slug=course_slug,user=user)
        subscribed_course.assessment_score = score
        subscribed_course.save()
    return Response({"score":score})

## enpoimt to restart course 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restartcourse(request , course_slug):
    ## make all completed modules in Subscribed courses = 0 
    my_course = Subscribed_courses.objects.get(course__slug=course_slug , user = request.user)
    my_course.completed_modules = 0
    my_course.save()
    return Response({'message':'Restart Course completed!'})

## get most 2 likes number courses 
class MostLikeCourses(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer

    def get_queryset(self):
        returned_data = Course.objects.order_by('-likes_number')[:2]
        return returned_data

## get most 2 compleated courses 
class MostCompletedCourses(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer

    def get_queryset(self):
        returned_data = Course.objects.order_by('-users_completed')[:2]
        return returned_data

## recomendition endpoint 
class RecomendationAPI(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer

    def get_queryset(self):
        # Get the categories of the courses the user is subscribed to
        user_courses = Subscribed_courses.objects.filter(user=self.request.user).order_by('-start_date')
        id_courses = []
        for course in user_courses:
            id_courses.append(course.course.pk)
        recomended_courses = Course.objects.filter(category = user_courses[0].course.category).order_by('-id').exclude(id__in=id_courses)[:2]
        return recomended_courses

# endpoint to create a new question with its answers 
class CreateQuestion(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Questions.objects.all()
    serializer_class = QuestionsSerializer

# endpoint to create quetions 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createQuestion(request, course_slug):
    course = Course.objects.get(slug=course_slug)
    data = request.data.copy()
    ## create question 
    question = Questions.objects.create(text=data['text'],course=course)
    question.save()
    for answer_data in data['answers']: 
        answer = Answers.objects.create(question=question , text= answer_data['text'] , is_correct = answer_data['is_correct'])
        answer.save()
    return Response({'message':'new question created'})
# list all answers 
class ListAnswersss(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnswerSubmistionSerializer
    queryset = Answers.objects.all()

#### list all questions ###
# class ListQuestion(ListAPIView):
#     serializer_class = QuestionsSerializer
#     queryset = Questions.objects.all()
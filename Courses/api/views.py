from rest_framework.decorators import api_view , permission_classes
from django.db import transaction
from rest_framework import filters
from .filters import CourseFilters
from django.db.models import Prefetch
from .pagination import CoursePagination, ModulePagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from Payment.api.permissions import HasActiveSubscription   
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView  , CreateAPIView
from Courses.models import Course, Module, Assessment , Subscribed_course, Answer, Question
from Courses.api.serializers import (CourseSerializer, AppliedCourseListSerializer, CourseDetailsSerializer,
                                      AppliedCourseDetailSerializer, AnswerSubmistionSerializer, QuestionsSerializer,
                                        ModuleSerializer, AssessmentSerializer, SubmitAnswersSerializer)

# endpoint to list all courses
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
        data = Subscribed_course.objects.filter(user=self.request.user)
        return data

## endpoint for course detail ##
class ShowCourseDetail(RetrieveAPIView):
    permission_classes = [HasActiveSubscription]
    lookup_field = 'course_slug'
    def get(self, request, course_slug):
        try:
            course = Subscribed_course.objects.get(user= request.user, course__slug=course_slug)
            serializer = AppliedCourseDetailSerializer(course)
        except:
            course  = Course.objects.get(slug=course_slug)
            serializer = CourseDetailsSerializer(course)
        finally:
            return Response(serializer.data)

## endpoint to apply on any course ##
@api_view(['POST'])
@permission_classes([HasActiveSubscription])
def apply_course(request,course_slug):
    course = Course.objects.get(slug=course_slug)
    user = request.user
    #check if the user is already subscribe to the course or create new subscription
    subscription , created = Subscribed_course.objects.get_or_create(user=user, course=course)
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

# endpoint let the user unlike a specific course
@api_view(['POST'])
@permission_classes([HasActiveSubscription])
def unlike_course(request ,course_slug):
    user = request.user
    course = Course.objects.get(slug=course_slug)
    if course.liked_users.filter(id=user.pk).exists():
        # using atomic transaction when doing multiple related operations are performed in sequence to
        # ensure that either both operations succeed or neither does
        with transaction.atomic():
            course.likes_number -= 1 
            course.liked_users.remove(user)
            course.save() 
            return Response({"message":f"you have unliked this course"})
    else:    
        return Response({"message":f"you did not like this course"})

## endpoint to get all liked courses for the requested user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def show_liked_course(request):
    ## query set to get courses liked for user
    course = Course.objects.filter(liked_users = request.user)
    
    if course:
        # serialize courses
        serializer = CourseSerializer(course, many=True,context={'request':request})
        return Response(serializer.data)
    return Response({"message":"no courses liked for you!"})


## endpoint to list all modules for each course 
@api_view(['GET'])
def ListModulesCourse(request, course_slug):
    all_modules = Module.objects.filter(course__slug = course_slug)
    completed_modules_ids = Subscribed_course.objects.get(course__slug = course_slug,user=request.user).completed_modules_ids
    paginator = ModulePagination()
    paginated_query = paginator.paginate_queryset(all_modules, request)
    module_serialized = ModuleSerializer(paginated_query,many=True)

    return Response({"modules":module_serialized.data,"completed_modules_ids":completed_modules_ids})
    

## complete module 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_module(request , course_slug , module_id):
    ## increament the number of completed modules for user in the course ##
    subscribed_course = Subscribed_course.objects.get(course__slug= course_slug , user = request.user)
    id = module_id
    modules = Module.objects.filter(course=subscribed_course.course).in_bulk(field_name='id')
    total_modules = len(modules)
    if id not in subscribed_course.completed_modules_ids and module_id in modules:
        with transaction.atomic():
            subscribed_course.completed_modules += 1 
            list_ids = subscribed_course.completed_modules_ids
            list_ids.append(id)
            if subscribed_course.completed_modules == total_modules:
                subscribed_course.status = 'Ready For Assessment'
            subscribed_course.save()
        return Response({"message":f"module completed"})
    else:
        return Response({"message":"you already completed this module or module is not exists the course"})

# uncomplete module
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def uncomplete_module(request , course_slug , module_id):
    # increment the number of completed modules for user in the course
    subscribed_course = Subscribed_course.objects.get(course__slug= course_slug , user = request.user )
    id = module_id
    if id in subscribed_course.completed_modules_ids:
        # using atomic transaction when doing multiple related operations are performed in sequence to
        # ensure that either both operations succeed or neither does
        with transaction.atomic(): 
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
    # Check if the user has finished their modules before attempting to access the assessment
    subscribed_course = Subscribed_course.objects.get(course__slug=course_slug, user=request.user.pk)
    if subscribed_course.status == 'in progress':
        return Response({"message": "You haven't finished your modules yet."})
    # Fetch the assessment object along with a random sample of 10 questions
    assessment = Assessment.objects.prefetch_related(
        Prefetch('questions', queryset=Question.objects.order_by('?')[:10], to_attr='random_questions')
        ).get(course__slug=course_slug)
    # Serialize and return the response
    serializer = AssessmentSerializer(assessment, context={'request': request})
    return Response(serializer.data)

## submit ansers 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submitAnswers(request, course_slug):
    user = request.user
    answers = Answer.objects.filter(question__assessment__course__slug=course_slug, is_correct=True).values_list('id', flat=True)
    serialized_data = AnswerSubmistionSerializer(answers, many=True).data
    serializer_submitted_answer = SubmitAnswersSerializer(data=request.data)
    if serializer_submitted_answer.is_valid():
        score = 0
        for answer in serialized_data:
            if answer['is_correct'] == True and answer['id'] in serializer_submitted_answer.data['answers'] :
                score += 1
        score = (score/10)*100
        if score > 50:
            ## add score to subscribed course attributes 
            subscribed_course = Subscribed_course.objects.get(course__slug=course_slug,user=user)
            course = Course.objects.get(slug=course_slug)
            # using atomic transaction when doing multiple related operations are performed
            with transaction.atomic(): 
                subscribed_course.assessment_score = score
                subscribed_course.status = 'completed'
                course.users_completed += 1
                subscribed_course.save()
            return Response({"score":score})
        else:
            return Response({"message":"your score is less than 50, you can't complete the course"})
    else:
        return Response(serializer_submitted_answer.errors)

# enpoimt to restart course 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restartcourse(request , course_slug):
    # make all completed modules in Subscribed courses = 0 
    my_course = Subscribed_course.objects.get(course__slug=course_slug, user = request.user)
    my_course.completed_modules = 0
    my_course.save()
    return Response({'message':'Restart Course completed!'})

# get most 2 likes number courses 
class MostLikeCourses(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer

    def get_queryset(self):
        returned_data = Course.objects.order_by('-likes_number')[:2]
        return returned_data

# get most 2 compleated courses 
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
        user_courses = Subscribed_course.objects.filter(user=self.request.user).order_by('-start_date')
        id_courses = []
        for course in user_courses:
            id_courses.append(course.course.pk)
        recomended_courses = Course.objects.filter(category = user_courses[0].course.category).order_by('-id').exclude(id__in=id_courses)[:2]
        return recomended_courses

# endpoint to create a new question with its answers 
class CreateQuestion(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Question.objects.all()
    serializer_class = QuestionsSerializer

# endpoint to create quetions 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createQuestion(request, course_slug):
    course = Course.objects.get(slug=course_slug)
    data = request.data.copy()
    # create question 
    question = Question.objects.create(text=data['text'],course=course)
    question.save()
    for answer_data in data['answers']: 
        answer = Answer.objects.create(question=question , text= answer_data['text'] , is_correct = answer_data['is_correct'])
        answer.save()
    return Response({'message':'new question created'})
# list all answers 
class ListAnswersss(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnswerSubmistionSerializer
    queryset = Answer.objects.all()

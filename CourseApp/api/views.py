from typing import Any
from django.db.models import Count
from Payment.api.permissions import HasActiveSubscription
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, UpdateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from django.views.generic.detail import DetailView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from CourseApp.models import Course, Module, Assessment, Section, AssessmentCompleted
from CourseApp.api.serializers import CourseSerializer, ModuleSerializer, AssmentsSerializer, SectionSerializer, AssessmentCompletedSerializer
from BlogApp.api.permissions import IsAdminOrReadOnly
from UserApp.models import User
from Payment.api.permissions import HasActiveSubscription


class CoursesListView(ListAPIView):
    permission_classes = [HasActiveSubscription]
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title']
    ordering_fields = ["likes_number", "subscriber_number", "completed"]

class CoursesDetailsView(DetailView):
    permission_classes = [HasActiveSubscription]
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    lookup_url_kwarg = 'id'

    def get_context_data(self,serializer, **kwargs: Any) -> dict[str, Any]:
        instance = serializer.instance 

        liked = False
        if instance.likes().filter(id=self.request.user.id).exists():
            liked = True
        subscribed = False

class UserCoursesView(ListAPIView):
    permission_classes = [HasActiveSubscription]
    serializer_class = CourseSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title']
    ordering_fields = ["likes_number", "subscriber_number", "completed"]

    def get_queryset(self):
        queryset = Course.objects.all()

        user_id = self.request.user.id
        queryset = queryset.filter(subscribed=user_id)

        return queryset

class MoudlesistView(ListAPIView):
    permission_classes = [HasActiveSubscription]
    serializer_class = ModuleSerializer
        
    def get_queryset(self):
        course_id = self.kwargs.get("courseid")
        return Module.objects.filter(course=course_id)
    
class AssmentsListView(ListAPIView):
    serializer_class = AssmentsSerializer
    permission_classes = [HasActiveSubscription]
    def get_queryset(self):
        module_id = self.kwargs.get("module")
        if module_id != None:
            return Assessment.objects.filter(module=module_id)
        return Assessment.objects.all()
        

class SectionUpdateView(UpdateAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    lookup_url_kwarg = 'id'
    permission_classes = [HasActiveSubscription]

    def perform_update(self, serializer):
        insstance = serializer.instance
        user = self.request.user

        if not insstance.completed.filter(pk=user.pk).exists():
            insstance.completed.add(user)
        else:
            insstance.completed.remove(user)
        
        serializer.save()

class CourseCreateView(CreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CourseSerializer

    def perform_create(self, serializer,):
        serializer.save(user=self.request.user)

class CourseUpdateView(RetrieveUpdateDestroyAPIView,):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CourseSerializer
  
    queryset = Course.objects.all()
    lookup_url_kwarg = "id"

    def perform_update(self, serializer):
        serializer.save()

class ModuleCreateView(CreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ModuleSerializer

    def perform_create(self, serializer):
        serializer.save()

class ModuleUpdateView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ModuleSerializer
    
    queryset = Module.objects.all()
    lookup_url_kwarg = "id"
    
    def perform_update(self, serializer):
        serializer.save()

    
class AssessmentCreateView(CreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = AssmentsSerializer
    
    def perform_create(self, serializer):
        serializer.save()

class AssessmentUpdateView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = AssmentsSerializer

    queryset = Module.objects.all()
    lookup_url_kwarg = "id"

    def perform_update(self, serializer):
        serializer.save()

class LikeView(UpdateAPIView):
    permission_classes = [HasActiveSubscription]

    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    lookup_url_kwarg = "id"

    # addes like if not and removes like if exists
    def perform_update(self, serializer):
        instance = serializer.instance
        user = self.request.user

        if not instance.likes.filter(pk=user.pk).exists():
            instance.likes.add(user)
            instance.likes_number += 1
        else:
            instance.likes.remove(user)
            instance.likes_number -= 1
        serializer.save()

class SubscribeView(UpdateAPIView):
    permission_classes = [HasActiveSubscription]

    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    lookup_url_kwarg = "id"

    # adds subscriber if not and removes if yes
    def perform_update(self, serializer):
        instance = serializer.instance
        user = self.request.user
        if not instance.subscribed.filter(pk=user.pk).exists():
            instance.subscribed.add(user)
            instance.subscriber_number += 1
        else:
            instance.subscribed.remove(user)
            instance.subscriber_number -= 1
        serializer.save()

class MarkMoudleView(CreateAPIView):
    permission_classes = [HasActiveSubscription]

    serializer_class = ModuleSerializer
    queryset = Module.objects.all()
    lookup_url_kwarg = "id"


    def perform_create(self,serializer):
        serializer.save(user=self.request.user)

#creates a new object to keep track of completion status
class MarkAssessmentView(CreateAPIView):
    permission_classes = [HasActiveSubscription]
    serializer_class = AssessmentCompletedSerializer

    def perform_create(self, serializer):
        user = self.request.user
        assessment = self.request.data.get("assessment")

        already_exists = AssessmentCompleted.objects.filter(user=user, assessment=assessment)
        if already_exists:
            return AssessmentCompleted.objects.filter(user=user, assessment=assessment)
        
        serializer.save(user=user)
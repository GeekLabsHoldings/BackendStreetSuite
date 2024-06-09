from django.urls import path
from .views import QuizList, RandomQuestion, CategoryView


urlpatterns = [
    path('', QuizList.as_view(), name='quiz'),
    path('categories/', CategoryView.as_view(), name="blog"),
    path('r/<str:topic>/', RandomQuestion.as_view(), name='random'),
]   
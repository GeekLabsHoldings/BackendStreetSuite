from django.urls import path
from .views import QuizList, Questions, CategoryView, QuizDetailView


urlpatterns = [
    path('', QuizList.as_view(), name='quiz'),
    path('categories/', CategoryView.as_view(), name="categories"),
    path('<int:pk>/',QuizDetailView.as_view(), name='quiz-detail'),
    path('<int:quiz_id>/questions/', Questions.as_view(), name='questions'),
]
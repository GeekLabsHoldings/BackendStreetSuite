from django.urls import path
from .views import PostChangeLog , ListChangeLog

urlpatterns =[
    path('post/',PostChangeLog.as_view()),
    path('list_all/',ListChangeLog.as_view()),
]

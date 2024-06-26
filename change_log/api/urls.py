from django.urls import path
from .views import PostChangeLog , ListChangeLog , PostMessage , ListMessage

urlpatterns =[
    path('post/',PostChangeLog.as_view()),
    path('list_all/',ListChangeLog.as_view()),
    path('post_feature/',PostMessage.as_view()),
    path('list_feature/',ListMessage.as_view()),
]

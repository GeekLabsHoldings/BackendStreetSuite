from django.urls import path 
from .views import PostMessage , ListMessages

urlpatterns = [
    path('post_message/', PostMessage.as_view(), name='PostMessage'),
    path('list_messages/', ListMessages.as_view(), name='ListMessages'),
    
]
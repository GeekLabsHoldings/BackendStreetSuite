from django.urls import path
from .views import AlertListView , test

urlpatterns = [
    path('', AlertListView.as_view() , name='list_alerts'),
    path('test/', test , name='test'),
    
]

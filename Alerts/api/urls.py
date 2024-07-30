from django.urls import path
from .views import AlertListView

urlpatterns = [
    path('', AlertListView.as_view() , name='list_alerts'),
    
]

from django.urls import path
from .views import AlertListView , test , earn , short_interset

urlpatterns = [
    path('', AlertListView.as_view() , name='list_alerts'),
    path('test/', test , name='test'),
    path('earn/', earn , name='earn'),
    path('short_interset/', short_interset , name='short_interset'),
    
]

from django.urls import path
from .views import ReviewList, AddReview


urlpatterns = [
    path('get_reviews/',ReviewList.as_view(), name='_getreviews'),
    path('create_review/',AddReview.as_view(), name='create_review'),
]
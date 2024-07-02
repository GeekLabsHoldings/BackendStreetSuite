from django.urls import path
from .views import ReviewList, AddReview, UpdateReview


urlpatterns = [
    path('get_reviews/',ReviewList.as_view(), name='_getreviews'),
    path('create_review/',AddReview.as_view(), name='create_review'),
    path('update_review/<int:id>',UpdateReview.as_view(), name='update_review'),
]
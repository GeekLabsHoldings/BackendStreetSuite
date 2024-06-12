from django.urls import path
from .views import Questions, CategoryView, SubCategoryList, SubCategoryDetailView, SubCatergoryCreateView


urlpatterns = [
    path('',SubCategoryList.as_view(), name='quiz'),
    path('categories/', CategoryView.as_view(), name="categories"),
    path('<int:pk>/',SubCategoryDetailView.as_view(), name='quiz-detail'),
    path('new/', SubCatergoryCreateView.as_view(), name= 'new-quiz'),
    path('<int:subcategory_id>/questions/', Questions.as_view(), name='questions'),
    
]
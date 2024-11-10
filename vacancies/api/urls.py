from django.urls import path
from .views import   list_applications , List_Vacancies   , VacancyDetailAdmin , VacancyDetailUser , PostCareer , ApplyVacancy

urlpatterns = [
    path('', List_Vacancies.as_view() , name="list_vacancies"),
    path('post-vacancy/', PostCareer.as_view() , name="post_vacancy"),
    path('admin/<str:slug>/', VacancyDetailAdmin.as_view() , name="VacancyDetail"),
    path('apply/<str:slug>/', ApplyVacancy.as_view() , name="apply"),
    path('<str:slug>/applications/', list_applications , name="list_applications"),
    
]
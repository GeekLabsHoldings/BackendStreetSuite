from django.urls import path
from .views import VacancyApplications , List_Vacancies , VacancyDetail , PostCareer , ApplyVacancy , VacancyEdit 

urlpatterns = [
    path('', List_Vacancies.as_view() , name="list_vacancies"),
    path('post-vacancy/', PostCareer.as_view() , name="post_vacancy"),
    path('<str:slug>/', VacancyDetail.as_view() , name="VacancyDetail"),
    path('admin/<str:slug>/', VacancyEdit.as_view() , name="VacancyEdit"),
    path('apply/<str:slug>/', ApplyVacancy.as_view() , name="apply"),
    path('applications/<str:slug>/', VacancyApplications.as_view() , name="list_applications"),
]
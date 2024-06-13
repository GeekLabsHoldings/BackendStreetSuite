from django.urls import path, include
from .views import post_vacancy , apply_vacancy , list_applications , List_Vacancies  ,List_Admin_Vacancies , VacancyDetailAdmin , VacancyDetailUser

urlpatterns = [
    path('post-vacancy/', post_vacancy , name="post_vacancy"),
    path('apply/<str:vacancy_slug>/', apply_vacancy , name="apply"),
    path('vacancy/<str:vacancy_slug>/applications/', list_applications , name="list_applications"),
    path('vacancy/', List_Vacancies.as_view() , name="list_vacancies"),
    path('vacancy/admin/', List_Admin_Vacancies.as_view() , name="List_Admin_Vacancies"),
    path('vacancy/admin/<str:slug>/', VacancyDetailAdmin.as_view() , name="VacancyDetail"),
    
]
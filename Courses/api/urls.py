from django.urls import path
from Courses.api import views
urlpatterns = [

    path("", views.CoursesListView.as_view(), name="courses_list"),
    path("mostlike/", views.MostLikeCourses.as_view(), name="most_like"),
    path("mostcomplete/", views.MostCompletedCourses.as_view(), name="most_complete"),
    path("recomendation/", views.RecomendationAPI.as_view(), name="recomendation"),
    path("likehistory/", views.show_liked_course, name="show_liked_user"),
    path("my_courses/", views.ShowMyCourses.as_view(), name="my_courses_inprogress"),
    path("create_question/<str:course_slug>/", views.createQuestion, name="create_question"),
    path("<str:course_slug>/", views.ShowCourseDetail.as_view(), name="course_details"),
    path("<str:course_slug>/apply/", views.apply_course, name="apply_course"),
    path("<str:course_slug>/like/", views.like_course, name="like_course"),
    path("<str:course_slug>/modules/", views.ListModulesCourse, name="list_modules"),
    path("<str:course_slug>/unlike/", views.unlike_course, name="unlike_course"),
    path("<str:course_slug>/<int:module_id>/complete/", views.complete_module, name="complete_module"),
    path("<str:course_slug>/<int:module_id>/uncomplete/", views.uncomplete_module, name="uncomplete_module"),
    path("<str:course_slug>/assessment/", views.get_assessment, name="get_assessment"),
    path("<str:course_slug>/assessment/submit/", views.submitAnswers, name="submit_answers"),
    path("<str:course_slug>/restart/", views.restartcourse, name="restart_course"),
]
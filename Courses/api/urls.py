from django.urls import path
from Courses.api import views
urlpatterns = [

    path("", views.CoursesListView.as_view(), name="courses_list"),
    # path("answers/", views.ListAnswersss.as_view(), name="answers"), ### test ##
    # path("questions/", views.ListQuestion.as_view(), name="questions"), ### test ##
    path("mostlike/", views.MostLikeCourses.as_view(), name="most_like"),
    path("mostcomplete/", views.MostCompletedCourses.as_view(), name="most_complete"),
    path("recomendation/", views.RecomendationAPI.as_view(), name="recomendation"),
    path("likehistory/", views.show_liked_course, name="show_liked_user"),
    path("my_courses/completed/", views.ShowMyCompletedCourses.as_view(), name="my_courses_completed"),
    path("my_courses/inprogress/", views.ShowMyInprogressCourses.as_view(), name="my_courses_inprogress"),
    path("<str:course_slug>/create_question/", views.createQuestion, name="create_question"),
    path("<str:slug>/apply/", views.apply_course, name="apply_course"),
    path("my_courses/<str:slug>/", views.GetMyCourse, name="retrive_my_course"),
    path("<str:slug>/", views.ShowCourseDetail.as_view(), name="course_detials"),
    path("<str:slug>/like/", views.like_course, name="like_course"),
    path("<str:slug>/modules/", views.ListModulesCourse.as_view(), name="list_modules"),
    path("<str:course_slug>/<str:module_slug>/complete/", views.complete_module, name="complete_module"),
    path("<str:course_slug>/<str:module_slug>/uncomplete/", views.uncomplete_module, name="uncomplete_module"),
    path("<int:course_id>/assesment/", views.get_assessment, name="get_assesment"),
    path("<slug:course_slug>/<int:assessment_id>/assesment/submet/", views.submetAnsers, name="submet_ansers"),
    path("<str:course_slug>/restart/", views.restartcourse, name="restart_course"),
]
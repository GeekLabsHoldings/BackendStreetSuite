from django.urls import path
from CourseApp.api import views
urlpatterns = [

    path("", views.CoursesListView.as_view(), name="courses"),
    path("<int:id>", views.CoursesListView.as_view(), name="course_detials"),
    # path("details/<int:id>", views.CoursesDetailsView.as_view(), name="course_detials"),
    path("user_courses/", views.UserCoursesView.as_view(), name="user_courses"),
    path("modules/<int:courseid>", views.MoudlesistView.as_view(), name="modules"),
    path("assessment/<int:module>", views.AssmentsListView.as_view(), name="assessment"),
    path("course_create/", views.CourseCreateView.as_view(), name="course_create"),
    path("course_update/<int:id>", views.CourseUpdateView.as_view(), name="course_update"),
    path("module_create/", views.ModuleCreateView.as_view(), name="module_create"),
    path("module_update/<int:id>", views.ModuleUpdateView.as_view(), name="module_update"),
    path("assessment_create/", views.AssessmentCreateView.as_view(), name="assessment_create"),
    path("assessment_update/<int:id>", views.AssessmentUpdateView.as_view(), name="assessment_update"),
    path("like/<int:id>", views.LikeView.as_view(), name="like"),
    path("subscribe/<int:id>", views.SubscribeView.as_view(), name="subscribe"),
    path("assessment_complete", views.MarkAssessmentView.as_view(), name="module_complete"),
    path("section_complete/<int:id>", views.SectionUpdateView.as_view(), name="mark_complete"),

]

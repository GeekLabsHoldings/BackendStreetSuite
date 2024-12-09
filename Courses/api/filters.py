from django_filters import rest_framework as filters
from Courses.models import Course


class CourseFilters(filters.FilterSet):
    level = filters.CharFilter(field_name="level")
    category = filters.CharFilter(field_name="courses_category")


    class Meta:
        model = Course
        fields = ["level", "category"]

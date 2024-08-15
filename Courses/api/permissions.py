from rest_framework.permissions import BasePermission, SAFE_METHODS
from Courses.models import Subscribed_courses , CompletedModules , Module

## PERMISSION TO OPEN Assessment ##
class AssessmentIsValid(BasePermission):
    def has_permission(self , request , view ):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        all_modules_titles = set(Module.objects.filter(course=obj.course).values_list('title',flat=True))
        completed_modules_for_user = set(CompletedModules.objects.filter(user=request.user).values_list('module__title' , flat=True))
        ## check if all modules titles is all covered completed_modules_for_user ##
        return all_modules_titles.issubset(completed_modules_for_user)



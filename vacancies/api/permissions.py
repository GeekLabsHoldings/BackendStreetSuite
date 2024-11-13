from rest_framework.permissions import BasePermission , SAFE_METHODS

##  permission to make only admin post vacancies ##
class IsAdminUser(BasePermission):
    """
        only admins can post vacancies 
    """
    def has_permission(self , request , view ):
        if request.user.is_authenticated:
            if request.method in SAFE_METHODS:
                return True
            if hasattr(request.user, 'profile') and request.user.profile.is_admin:
                return True
        return False
    

from rest_framework.permissions import BasePermission , SAFE_METHODS

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method in SAFE_METHODS:
                if hasattr(request.user, 'profile') and request.user.profile.is_admin:
                    return True

        return False
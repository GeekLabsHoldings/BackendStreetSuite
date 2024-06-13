from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSubscribed(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if  request.user.userpayment.product:
                return True
            else:
                return False
        else: return False
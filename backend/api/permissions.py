from rest_framework.permissions import BasePermission


class IsPaid(BasePermission):
 

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
       
        from .models import UserProfile

        try:
            return bool(UserProfile.objects.get(user=user).has_access)
        except UserProfile.DoesNotExist:
            return False


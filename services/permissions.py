from rest_framework import permissions

class IsFreelancer(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'freelancer')
    
class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'client')
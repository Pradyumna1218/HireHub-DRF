from rest_framework import permissions

class IsFreelancer(permissions.BasePermission):
    '''Check if the user is freelancer'''
    def has_permission(self, request, view):
        return hasattr(request.user, 'freelancer')
    
class IsClient(permissions.BasePermission):
    '''Check if the user is client'''
    def has_permission(self, request, view):
        return hasattr(request.user, 'client')
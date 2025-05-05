from rest_framework import permissions
from users.models import Client, Freelancer

class IsClientOrFreelancer(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            print("User is not authenticated.")
            return False
        
        print(f"Checking user: {user.username}, ID: {user.id}")

        is_client = Client.objects.filter(user=user).exists()
        is_freelancer = Freelancer.objects.filter(user=user).exists()

        print("Is Client:", is_client)
        print("Is Freelancer:", is_freelancer)

        return is_client or is_freelancer

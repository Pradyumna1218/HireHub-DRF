from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category,Service
from .serializers import CategorySerializer, ServiceSerializer
from .permissions import IsFreelancer, IsClient
from rest_framework import status
from users.models import Freelancer
from rest_framework.permissions import IsAuthenticated


class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
class FreelancerServiceView(APIView):
    permission_classes = [IsFreelancer, IsAuthenticated]

    def post(self, request):
        freelancer = Freelancer.objects.get(user=request.user)
        
        request.data['freelancer'] = freelancer.user.id  # Set the ID instead of the instance directly
        
        serializer = ServiceSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ClientServiceView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        queryset = Service.objects.all()
        serializer = ServiceSerializer(queryset, many= True)
        return Response(serializer.data, status=status.HTTP_200_OK)
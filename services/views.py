from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category,Service
from .serializers import (
    CategorySerializer, 
    ServiceSerializer,
    FreelancerServiceDetailSerializer,
    ServiceSearchSerializer
    )
from .permissions import IsFreelancer, IsClient
from rest_framework import status
from users.models import Freelancer
from rest_framework.permissions import IsAuthenticated
from .services import ServiceSearcher

class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
class FreelancerServiceView(APIView):
    permission_classes = [IsFreelancer, IsAuthenticated]

    def post(self, request):
        serializer = ServiceSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ClientServiceView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        serializer = ServiceSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        categories = serializer.validated_data.get('categories', [])
        skills = serializer.validated_data.get('skills', [])

        searcher = ServiceSearcher(categories= categories, skills=skills)
        queryset_all, queryset_by_category, queryset_by_skills = searcher.search()

        if queryset_all is not None:
            all_services_serializer = ServiceSerializer(queryset_all, many = True)
            return Response({
                "all_services": all_services_serializer.data
            }, status=status.HTTP_200_OK)

        category_serializer = ServiceSerializer(queryset_by_category, many=True)
        skill_serializer = ServiceSerializer(queryset_by_skills, many=True)

        return Response({
            "category_matches": category_serializer.data,
            "skill_matches": skill_serializer.data,
        }, status=status.HTTP_200_OK)
    
class FreelancerServiceDetailView(APIView):
    def get(self, request, pk):
        try:
            service = Service.objects.get(id=pk, freelancer__user=request.user)
        except Service.DoesNotExist:
            return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = FreelancerServiceDetailSerializer(service)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        try:
            service = Service.objects.get(id = pk, freelancer__user = request.user)
        except Service.DoesNotExist:
            return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = FreelancerServiceDetailSerializer(service, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    

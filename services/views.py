from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category,Service
from .serializers import (
    CategorySerializer, 
    ServiceSerializer,
    FreelancerServiceDetailSerializer,
    ServiceSearchSerializer,
    ProposalCreateSerializer
    )
from .permissions import IsFreelancer, IsClient
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from users.models import Freelancer

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
    def get(self, request):
        serializer = ServiceSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        queryset = Service.objects.filter(is_active=True)

        result = {
            "categories_result": [],
            "skills_result": [],
        }

        if 'categories' in data and data['categories']:
            categories_queryset = queryset.filter(
                categories__name__in=data['categories']
            ).distinct()
            result['categories_result'] = ServiceSerializer(categories_queryset, many=True).data

        if 'skills' in data and data['skills']:
            skills_queryset = queryset.filter(
                freelancer__skills__name__in=data['skills']
            ).distinct()
            result['skills_result'] = ServiceSerializer(skills_queryset, many=True).data

        return Response(result)

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

class ClientServiceDetailView(APIView):
    permission_classes = [IsClient]

    def get(self, request, pk):
        try:
            service = Service.objects.get(id=pk)
        except Service.DoesNotExist:
            return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

        service_serializer = FreelancerServiceDetailSerializer(service)

        return Response({
            "service": service_serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request, pk):        
        try:
            service = Service.objects.get(id=pk)
        except Service.DoesNotExist:
            return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProposalCreateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(service=service, client=request.user.client)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
        

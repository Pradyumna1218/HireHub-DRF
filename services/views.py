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
from rest_framework.permissions import IsAuthenticated
from .services import ServiceSearcher
from payments.serializers import OrderSerializer
from payments.models import Order
from users.models import Client

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
    

class ClientServiceDetailView(APIView):
    permission_classes = [IsClient]

    def get(self, request, pk):
        try:
            service = Service.objects.get(id=pk)
            order = Order.objects.filter(client__user = request.user, service= service)
        except Service.DoesNotExist:
            return Response({"error": "Didn't find the service"}, status=status.HTTP_404_NOT_FOUND)
        
        service_serializer = FreelancerServiceDetailSerializer(service)
        orders_serializer = OrderSerializer(order, many=True)

        return Response({
            "service": service_serializer.data,
            "orders": orders_serializer.data,
        }, status=status.HTTP_200_OK)
    
    def post(self, request, pk):
        try:
            service = Service.objects.get(id=pk)
        except Service.DoesNotExist:
            return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            client = Client.objects.get(user=request.user)
        except Client.DoesNotExist:
            return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        data['client'] = client.pk
        data['service'] = service.id  

        serializer = OrderSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
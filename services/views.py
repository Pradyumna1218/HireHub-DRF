from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category,Service, Proposal
from .serializers import (
    CategorySerializer, 
    ServiceSerializer,
    FreelancerServiceDetailSerializer,
    ServiceSearchSerializer,
    ProposalCreateSerializer,
    FreelancerProposalSerializer
    )
from .permissions import IsFreelancer, IsClient
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from payments.models import Order
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404


def get_service_queryset():
    """
    Returns a queryset of Service objects with related freelancer,
    user, categories, and freelancer skills prefetched for efficiency.
    """
     
    return Service.objects.select_related(
        'freelancer',
        'freelancer__user'
    ).prefetch_related(
        'categories',
        'freelancer__skills'
    )

def get_freelancer_proposals(user):
    """
    Returns a queryset of Proposal objects for the given freelancer user,
    with related service and client prefetched.
    """

    return Proposal.objects.filter(
        freelancer = user.freelancer
    ).select_related(
        "service",
        "client"
    )
class CategoryListView(APIView):
    """
    GET: List all available categories.
    """

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
class FreelancerServiceView(APIView):
    """
    POST: Allow authenticated freelancers to create a new service.
    Permission: IsFreelancer
    """

    permission_classes = [IsFreelancer]

    def post(self, request):
        serializer = ServiceSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ClientServiceView(APIView):
    """
    GET: Allow clients to search services by categories and/or skills.
    Returns matching services grouped by categories and skills.
    """
    permission_classes = [IsClient]

    def get(self, request):
        serializer = ServiceSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        queryset = get_service_queryset()

        if not data.get('categories') and not data.get('skills'):
            return Response(ServiceSerializer(queryset, many=True).data)
        
        result = {
            "categories_result": [],
            "skills_result": [],
        }

        if 'categories' in data:
            categories_queryset = queryset.filter(
                categories__name__in=data['categories']
            )
            result['categories_result'] = ServiceSerializer(categories_queryset, many=True).data

        if 'skills' in data:
            skills_queryset = queryset.filter(
                freelancer__skills__name__in=data['skills']
            )
            result['skills_result'] = ServiceSerializer(skills_queryset, many=True).data

        return Response(result)

class FreelancerServiceDetailView(APIView):
    """
    GET: Retrieve details of a specific service owned by the authenticated freelancer.
    PATCH: Partially update a specific service owned by the authenticated freelancer.
    Permission: IsFreelancer
    """

    permission_classes = [IsFreelancer]

    def get(self, request, pk):
        queryset = get_service_queryset()
        service = get_object_or_404(queryset, id=pk, freelancer__user=request.user)
        return Response(
            ServiceSerializer(service).data, 
            status=status.HTTP_200_OK
        )
    
    def patch(self, request, pk):
        queryset = get_service_queryset()
        service = get_object_or_404(queryset, id=pk, freelancer__user=request.user)
        serializer = FreelancerServiceDetailSerializer(service, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ClientServiceDetailView(APIView):
    """
    GET: Retrieve detailed info of a service.
    POST: Create a proposal for the service by the authenticated client.
    Permission: IsClient
    """

    permission_classes = [IsClient]

    def get(self, request, pk):
        queryset = get_service_queryset()
        service = get_object_or_404(queryset, id=pk)

        service_serializer = FreelancerServiceDetailSerializer(service)

        return Response({
            "service": service_serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request, pk):  
        queryset = get_service_queryset()    
        service = get_object_or_404(queryset, id=pk)

        serializer = ProposalCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(service=service, client=request.user.client)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FreelancerProposalListView(APIView):
    """
    GET: List all proposals received by the authenticated freelancer.
    Permission: IsFreelancer
    """

    permission_classes = [IsFreelancer]

    def get(self, request):
        proposals = get_freelancer_proposals(request.user)
        serializer = FreelancerProposalSerializer(proposals, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FreelancerProposalDetailView(APIView):
    """
    GET: Retrieve details of a specific proposal belonging to the authenticated freelancer.
    POST: Update the status of a proposal ('accepted' or 'rejected').
          If accepted, automatically creates an Order with a 7-day delivery.
    Permission: IsFreelancer
    """
    
    permission_classes = [IsFreelancer]

    def get(self, request, pk): 
        proposal = get_object_or_404(
            get_freelancer_proposals(request.user),
            id=pk
        )
        serializer = FreelancerProposalSerializer(proposal)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, pk):
        freelancer = request.user.freelancer
        proposal = get_object_or_404(
            Proposal, 
            id=pk, 
            freelancer=freelancer
        )

        new_status = request.data.get("status")
        if new_status not in ["accepted", "rejected"]:
            return Response(
                {"error": "Status must be either 'accepted' or 'rejected'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        proposal.status = new_status
        proposal.save()

        if new_status == "accepted":
            if hasattr(proposal, 'order'):
                return Response(
                    {"message": "Order already exists for this proposal."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            Order.objects.create(
                proposal=proposal,
                client=proposal.client,
                freelancer=proposal.freelancer,
                service=proposal.service,
                total_amount=proposal.proposed_price,
                delivery_date=timezone.now() + timedelta(days=7)
            )

        return Response(
            {"message": f"Proposal {new_status}."}, 
            status=status.HTTP_200_OK
        )
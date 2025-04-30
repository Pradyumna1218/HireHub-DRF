from django.urls import path
from .views import (
    CategoryListView, 
    FreelancerServiceView, 
    ClientServiceView,
    FreelancerServiceDetailView
        )

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('freelancer/services/', FreelancerServiceView.as_view(), name='freelancer-services'),
    path('client/services/', ClientServiceView.as_view(), name='freelancer-services'),
    path('freelancer/services/<int:pk>/', FreelancerServiceDetailView.as_view(), name='freelancer-service-detail'),
]
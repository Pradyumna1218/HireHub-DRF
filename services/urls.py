from django.urls import path
from .views import (CategoryListView, 
                    FreelancerServiceView, 
                    ClientServiceView
                    )

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('freelancer/services/', FreelancerServiceView.as_view(), name='freelancer-services'),
    path('client/services/', ClientServiceView.as_view(), name='freelancer-services'),

]
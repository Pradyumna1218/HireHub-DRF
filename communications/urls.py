# communications/urls.py
from django.urls import path
from .views import ChatHistoryView, ReviewCreateView

urlpatterns = [
    path('chat/history/<str:username>/', ChatHistoryView.as_view(), name='chat-history'),
    path('reviews/create/<int:order_id>/', ReviewCreateView.as_view(), name='review-create'),
]

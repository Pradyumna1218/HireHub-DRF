# communications/urls.py
from django.urls import path
from .views import ChatHistoryView

urlpatterns = [
    path('chat/history/<str:username>/', ChatHistoryView.as_view(), name='chat-history'),
]

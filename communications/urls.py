from django.urls import path
from .views import SendMessageView, ChatMessageView

urlpatterns = [
    path("send/", SendMessageView.as_view(), name="send_message"),
    path("chat/<str:username>/", ChatMessageView.as_view(), name="chat_messages"),
]

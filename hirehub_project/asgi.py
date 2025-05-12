import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hirehub_project.settings')

import django
django.setup()  # 🛠️ Required before anything else that uses Django ORM

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from communications.routing import websocket_urlpatterns

from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

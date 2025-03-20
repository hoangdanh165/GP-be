import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from channels.routing import ProtocolTypeRouter, URLRouter
from chat.socket import app as socket_app

from django.core.asgi import get_asgi_application



application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": socket_app,
})

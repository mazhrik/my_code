# from channels.routing import ProtocolTypeRouter, URLRouter
# from core_management import routing

# application = ProtocolTypeRouter({
#     'http': URLRouter(routing.urlpatterns),
# })


import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from target_management.consumers import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'OCS_Rest.settings')

application = get_asgi_application()
ws_patterns = [
    path("ws/test/", TestConsumer.as_asgi() ),
] 

application = ProtocolTypeRouter({
    'websocket' : URLRouter(ws_patterns)
})
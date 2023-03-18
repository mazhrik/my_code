"""
ASGI config for OCS_Rest project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from target_management.consumers import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'OCS_Rest.settings')

application = get_asgi_application()

ws_patterns = [
    path("ws/test/", TestConsumer.as_asgi())
]


application = ProtocolTypeRouter({
    'websocket' : URLRouter(ws_patterns)
})
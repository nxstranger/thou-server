# chat/routing.py
from django.urls import re_path

from .socket import socket

websocket_urlpatterns = [
    re_path(r'^private/$', socket.ChatConsumer.as_asgi()),
]

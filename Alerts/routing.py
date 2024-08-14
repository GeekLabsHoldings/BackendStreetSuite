from django.urls import path
from .consumers import WebSocketConsumer

ws_urlpatterns = [
    path('ws/alerts/', WebSocketConsumer.as_asgi()),
]
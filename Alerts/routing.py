from django.urls import path
from .consumers import WebSocketConsumer
from BlogApp.consumers import BlogWSConsumer

ws_urlpatterns = [
    path('ws/alerts/', WebSocketConsumer.as_asgi()),
    path('ws/blogs/', BlogWSConsumer.as_asgi()),
]
from django.urls import re_path
from .consumers import GameConsumer

websocket_urlpatterns = [
    re_path(r'ws/games/(?P<room_name>[^/]+)/$', GameConsumer.as_asgi()),
]
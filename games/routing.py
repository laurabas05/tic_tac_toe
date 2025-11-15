from django.urls import re_path
from .consumers import GameConsumer

websocket_urlpatterns = [
    re_path(r'ws/tic_tac_toe/$', GameConsumer.as_asgi()),
]
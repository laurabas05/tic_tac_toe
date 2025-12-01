from django.urls import path
from .views import get_joke

urlpatterns = [
    path("", get_joke, name="get_joke"),
]
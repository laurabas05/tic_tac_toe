from django.urls import path
from . import views

app_name = 'games'
urlpatterns = [
    path('', views.game_list, name='list'),
    path('create/', views.create_game, name='create'),
    path('<int:pk>/', views.game_detail, name='detail'),
    path('<int:pk>/close/', views.close_game, name='close')
]
from django.urls import path
from . import views

app_name = 'games'
urlpatterns = [
    path('list/', views.game_list, name='list'),
    path('create/', views.create_game, name='create'),
    path('<int:game_id>/', views.game_detail, name='detail'),
    path('close/', views.close_game, name='close')
]
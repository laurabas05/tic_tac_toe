from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.get_server_status, name='status'),
    path('errors/', views.get_errors, name='errors'),
    path('error/<int:code>/', views.get_error_from_code, name='error_by_code'),
    path('error/', views.create_error, name='create_error'),
    path('object/<int:id>/', views.object_update, name='object_update'),
]
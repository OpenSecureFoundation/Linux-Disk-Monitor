from django.urls import path
from . import views

urlpatterns = [
    # Pages principales
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('login/', views.login, name='login'),

    # Gestion des disques
    path('disk/start/<str:disk_name>/', views.start_disk, name='start_disk'),
    path('disk/stop/<str:disk_name>/', views.stop_disk, name='stop_disk'),
    path('disk/stats/<str:disk_name>/', views.disk_stats, name='disk_stats'),
    path('disk/usage/<str:disk_name>/', views.disk_usage, name='disk_usage'),
    path('disk/files/<str:disk_name>/', views.disk_open_files, name='disk_files'),
]
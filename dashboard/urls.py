"""
URL configuration for dashboard app
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.global_dashboard, name='global_dashboard'),
    path('gallery/', views.global_gallery, name='global_gallery'),
    path('statistics/', views.global_statistics, name='global_statistics'),
    path('participants/', views.all_participants, name='all_participants'),
]

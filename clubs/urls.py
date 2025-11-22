"""
URL configuration for clubs app
"""
from django.urls import path
from . import views

app_name = 'clubs'

urlpatterns = [
    # Club pages
    path('', views.club_list, name='club_list'),
    path('<slug:slug>/', views.club_detail, name='club_detail'),
    path('<slug:slug>/activities/', views.club_activities, name='club_activities'),
    path('<slug:slug>/members/', views.club_members, name='club_members'),
    path('<slug:slug>/action-plans/', views.club_action_plans, name='club_action_plans'),
    
    # Activity pages
    path('activity/<int:pk>/', views.activity_detail, name='activity_detail'),
    path('activity/<int:pk>/gallery/', views.activity_gallery, name='activity_gallery'),
]

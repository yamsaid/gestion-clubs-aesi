"""
Core URL configuration
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('guide/', views.user_guide, name='user_guide'),
    path('style-guide/', views.style_guide, name='style_guide'),
    path('mobile-test/', views.mobile_test, name='mobile_test'),
]

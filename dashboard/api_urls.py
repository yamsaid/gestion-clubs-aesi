"""
API URL configuration for dashboard app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('global-stats/', views.global_stats_api, name='global_stats_api'),
    path('club-stats/', views.club_stats_api, name='club_stats_api'),
    path('participation-trends/', views.participation_trends_api, name='participation_trends_api'),
    path('top-participants/', views.top_participants_api, name='top_participants_api'),
    path('financial-summary/', views.financial_summary_api, name='financial_summary_api'),
]

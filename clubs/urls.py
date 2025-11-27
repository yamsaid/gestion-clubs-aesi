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
    path('<slug:slug>/activities/add/', views.add_activity, name='add_activity'),
    path('<slug:slug>/activities/<int:activity_id>/edit/', views.edit_activity, name='edit_activity'),
    path('<slug:slug>/activities/<int:activity_id>/delete/', views.delete_activity, name='delete_activity'),
    path('<slug:slug>/members/', views.club_members, name='club_members'),
    path('<slug:slug>/bureau/', views.club_bureau, name='club_bureau'),
    path('<slug:slug>/participants/', views.club_participants, name='club_participants'),
    path('<slug:slug>/programs/', views.club_programs, name='club_programs'),
    path('<slug:slug>/budget/', views.club_budget, name='club_budget'),
    path('<slug:slug>/budget/add/', views.add_expense, name='add_expense'),
    path('<slug:slug>/form-generator/', views.club_form_generator, name='club_form_generator'),
    path('<slug:slug>/form-generator/generate/', views.generate_participation_form, name='generate_form'),
    path('<slug:slug>/dashboard/', views.club_dashboard, name='club_dashboard'),
    path('<slug:slug>/action-plans/', views.club_action_plans, name='club_action_plans'),
    
    # Activity pages
    path('activity/<int:pk>/', views.activity_detail, name='activity_detail'),
    path('activity/<int:pk>/gallery/', views.activity_gallery, name='activity_gallery'),
    
    # Task actions
    path('task/<int:task_id>/toggle/', views.toggle_task_completion, name='toggle_task_completion'),
]

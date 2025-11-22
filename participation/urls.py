"""
URL configuration for participation app
"""
from django.urls import path
from . import views

app_name = 'participation'

urlpatterns = [
    # OTP generation and verification
    path('generate-otp/<int:activity_id>/', views.generate_otp_view, name='generate_otp'),
    path('verify-otp/<int:activity_id>/', views.verify_otp_view, name='verify_otp'),
    
    # Participation form
    path('form/<int:activity_id>/', views.participation_form, name='participation_form'),
    path('submit/<int:activity_id>/', views.submit_participation, name='submit_participation'),
    
    # Participant list
    path('list/<int:activity_id>/', views.participant_list, name='participant_list'),
]

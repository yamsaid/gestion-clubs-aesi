"""
API URL configuration for participation app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParticipationViewSet, generate_otp_api, verify_otp_api

router = DefaultRouter()
router.register(r'participations', ParticipationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate-otp/<int:activity_id>/', generate_otp_api, name='generate_otp_api'),
    path('verify-otp/', verify_otp_api, name='verify_otp_api'),
]

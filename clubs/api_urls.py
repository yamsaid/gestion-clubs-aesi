"""
API URL configuration for clubs app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClubViewSet, ActivityViewSet, ActionPlanViewSet,
    TaskViewSet, CompetitionViewSet
)

router = DefaultRouter()
router.register(r'clubs', ClubViewSet)
router.register(r'activities', ActivityViewSet)
router.register(r'action-plans', ActionPlanViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'competitions', CompetitionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

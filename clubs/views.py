"""
Views for clubs app
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Club, Activity, ActionPlan, Task, Competition, ClubMember
from .serializers import (
    ClubSerializer, ActivitySerializer, ActionPlanSerializer,
    TaskSerializer, CompetitionSerializer
)


# Template views
def club_list(request):
    """List all clubs"""
    clubs = Club.objects.filter(is_active=True)
    return render(request, 'clubs/club_list.html', {'clubs': clubs})


def club_detail(request, slug):
    """Club detail page"""
    club = get_object_or_404(Club, slug=slug)
    recent_activities = club.activities.filter(status='COMPLETED')[:5]
    members = club.members.filter(is_active=True)
    
    context = {
        'club': club,
        'recent_activities': recent_activities,
        'members': members,
    }
    return render(request, 'clubs/club_detail.html', context)


def club_activities(request, slug):
    """Club activities page"""
    club = get_object_or_404(Club, slug=slug)
    activities = club.activities.all()
    
    context = {
        'club': club,
        'activities': activities,
    }
    return render(request, 'clubs/club_activities.html', context)


def club_members(request, slug):
    """Club members page"""
    club = get_object_or_404(Club, slug=slug)
    members = club.members.filter(is_active=True)
    
    context = {
        'club': club,
        'members': members,
    }
    return render(request, 'clubs/club_members.html', context)


@login_required
def club_action_plans(request, slug):
    """Club action plans page"""
    club = get_object_or_404(Club, slug=slug)
    action_plans = club.action_plans.all()
    
    context = {
        'club': club,
        'action_plans': action_plans,
    }
    return render(request, 'clubs/club_action_plans.html', context)


def activity_detail(request, pk):
    """Activity detail page"""
    activity = get_object_or_404(Activity, pk=pk)
    photos = activity.photos.all()
    competitions = activity.competitions.all()
    
    context = {
        'activity': activity,
        'photos': photos,
        'competitions': competitions,
    }
    return render(request, 'clubs/activity_detail.html', context)


def activity_gallery(request, pk):
    """Activity gallery page"""
    activity = get_object_or_404(Activity, pk=pk)
    photos = activity.photos.all()
    
    context = {
        'activity': activity,
        'photos': photos,
    }
    return render(request, 'clubs/activity_gallery.html', context)


# API ViewSets
class ClubViewSet(viewsets.ModelViewSet):
    """ViewSet for Club model"""
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'is_active']


class ActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for Activity model"""
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['club', 'status', 'date']


class ActionPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for ActionPlan model"""
    queryset = ActionPlan.objects.all()
    serializer_class = ActionPlanSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['club']


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task model"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['action_plan', 'is_completed', 'assigned_to']


class CompetitionViewSet(viewsets.ModelViewSet):
    """ViewSet for Competition model"""
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activity']

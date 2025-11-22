"""
Serializers for clubs app
"""
from rest_framework import serializers
from .models import (
    Club, ClubMember, ActionPlan, Task, Activity,
    ActivityPhoto, Competition, Winner, MemberAttendance
)
from users.serializers import UserMinimalSerializer


class ClubSerializer(serializers.ModelSerializer):
    """Serializer for Club model"""
    execution_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Club
        fields = [
            'id', 'name', 'slug', 'type', 'description', 'logo',
            'cover_image', 'email', 'phone', 'facebook_url',
            'twitter_url', 'instagram_url', 'is_active',
            'execution_rate', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ClubMemberSerializer(serializers.ModelSerializer):
    """Serializer for ClubMember model"""
    user = UserMinimalSerializer(read_only=True)
    club_name = serializers.CharField(source='club.name', read_only=True)
    
    class Meta:
        model = ClubMember
        fields = [
            'id', 'club', 'club_name', 'user', 'position',
            'start_date', 'end_date', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    assigned_to_name = serializers.CharField(
        source='assigned_to.user.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Task
        fields = [
            'id', 'action_plan', 'title', 'description',
            'assigned_to', 'assigned_to_name', 'due_date',
            'is_completed', 'completed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ActionPlanSerializer(serializers.ModelSerializer):
    """Serializer for ActionPlan model"""
    club_name = serializers.CharField(source='club.name', read_only=True)
    completion_rate = serializers.ReadOnlyField()
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = ActionPlan
        fields = [
            'id', 'club', 'club_name', 'title', 'description',
            'start_date', 'end_date', 'completion_rate',
            'tasks', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ActivityPhotoSerializer(serializers.ModelSerializer):
    """Serializer for ActivityPhoto model"""
    uploaded_by = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = ActivityPhoto
        fields = ['id', 'activity', 'image', 'caption', 'uploaded_by', 'created_at']
        read_only_fields = ['id', 'created_at']


class WinnerSerializer(serializers.ModelSerializer):
    """Serializer for Winner model"""
    participant = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = Winner
        fields = ['id', 'competition', 'participant', 'rank', 'prize', 'created_at']
        read_only_fields = ['id', 'created_at']


class CompetitionSerializer(serializers.ModelSerializer):
    """Serializer for Competition model"""
    winners = WinnerSerializer(many=True, read_only=True)
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    
    class Meta:
        model = Competition
        fields = [
            'id', 'activity', 'activity_title', 'name',
            'description', 'winners', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for Activity model"""
    club_name = serializers.CharField(source='club.name', read_only=True)
    participants_count = serializers.ReadOnlyField()
    photos = ActivityPhotoSerializer(many=True, read_only=True)
    competitions = CompetitionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Activity
        fields = [
            'id', 'club', 'club_name', 'title', 'description',
            'theme', 'date', 'time', 'location', 'status',
            'otp_enabled', 'difficulties', 'cover_image',
            'participants_count', 'photos', 'competitions', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MemberAttendanceSerializer(serializers.ModelSerializer):
    """Serializer for MemberAttendance model"""
    member_name = serializers.CharField(
        source='member.user.get_full_name',
        read_only=True
    )
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    
    class Meta:
        model = MemberAttendance
        fields = [
            'id', 'member', 'member_name', 'activity',
            'activity_title', 'is_present', 'marked_by',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

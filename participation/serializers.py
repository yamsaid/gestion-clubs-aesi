"""
Serializers for participation app
"""
from rest_framework import serializers
from .models import Participation, ParticipationStats
from users.serializers import UserMinimalSerializer


class ParticipationSerializer(serializers.ModelSerializer):
    """Serializer for Participation model"""
    user = UserMinimalSerializer(read_only=True)
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    club_name = serializers.CharField(source='activity.club.name', read_only=True)
    is_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = Participation
        fields = [
            'id', 'activity', 'activity_title', 'club_name', 'user',
            'otp_verified', 'otp_verified_at', 'appreciation',
            'suggestion', 'rating', 'photo1', 'photo2', 'photo3',
            'submitted_at', 'is_completed', 'created_at'
        ]
        read_only_fields = [
            'id', 'otp_verified', 'otp_verified_at',
            'submitted_at', 'created_at'
        ]


class ParticipationStatsSerializer(serializers.ModelSerializer):
    """Serializer for ParticipationStats model"""
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = ParticipationStats
        fields = [
            'id', 'user', 'total_participations', 'average_rating',
            'informatique_count', 'anglais_count', 'art_oratoire_count',
            'sport_count', 'total_wins', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']

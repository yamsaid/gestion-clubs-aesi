"""
Views for dashboard app
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache

from clubs.models import Club, Activity, Winner, ActivityPhoto
from participation.models import Participation, ParticipationStats
from finances.models import Transaction, CashBalance
from users.models import User


# Template views
def global_dashboard(request):
    """Global dashboard page"""
    
    # Get cached data or compute
    cache_key = 'global_dashboard_data'
    dashboard_data = cache.get(cache_key)
    
    if not dashboard_data:
        clubs = Club.objects.filter(is_active=True)
        
        # Aggregate statistics
        total_activities = Activity.objects.filter(status='COMPLETED').count()
        total_participants = Participation.objects.filter(otp_verified=True).count()
        total_clubs = clubs.count()
        
        # Recent activities
        recent_activities = Activity.objects.filter(
            status='COMPLETED'
        ).select_related('club')[:10]
        
        # Club execution rates
        club_stats = []
        for club in clubs:
            club_stats.append({
                'club': club,
                'execution_rate': club.execution_rate,
                'activities_count': club.activities.filter(status='COMPLETED').count(),
                'participants_count': Participation.objects.filter(
                    activity__club=club,
                    otp_verified=True
                ).count()
            })
        
        dashboard_data = {
            'total_activities': total_activities,
            'total_participants': total_participants,
            'total_clubs': total_clubs,
            'recent_activities': recent_activities,
            'club_stats': club_stats,
        }
        
        # Cache for 15 minutes
        cache.set(cache_key, dashboard_data, 900)
    
    context = dashboard_data
    
    return render(request, 'dashboard/global_dashboard.html', context)


def global_gallery(request):
    """Global gallery page with all activity photos"""
    
    # Get all photos with filters
    photos = ActivityPhoto.objects.select_related(
        'activity', 'activity__club', 'uploaded_by'
    ).order_by('-created_at')
    
    # Filter by club if specified
    club_filter = request.GET.get('club')
    if club_filter:
        photos = photos.filter(activity__club__slug=club_filter)
    
    clubs = Club.objects.filter(is_active=True)
    
    context = {
        'photos': photos,
        'clubs': clubs,
        'selected_club': club_filter,
    }
    
    return render(request, 'dashboard/global_gallery.html', context)


@login_required
def global_statistics(request):
    """Global statistics page (restricted to AESI executives)"""
    
    if not (request.user.is_aesi_executive or request.user.is_staff):
        return render(request, 'dashboard/access_denied.html')
    
    # Compute various statistics
    clubs = Club.objects.filter(is_active=True)
    
    # Participation trends
    last_6_months = timezone.now() - timedelta(days=180)
    participation_by_month = Participation.objects.filter(
        created_at__gte=last_6_months,
        otp_verified=True
    ).extra(
        select={'month': "DATE_TRUNC('month', created_at)"}
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    # Top participants across all clubs
    top_participants = ParticipationStats.objects.order_by('-total_participations')[:10]
    
    # Recent winners
    recent_winners = Winner.objects.select_related(
        'participant', 'competition', 'competition__activity'
    ).order_by('-created_at')[:20]
    
    context = {
        'clubs': clubs,
        'participation_by_month': participation_by_month,
        'top_participants': top_participants,
        'recent_winners': recent_winners,
    }
    
    return render(request, 'dashboard/global_statistics.html', context)


@login_required
def all_participants(request):
    """All participants page (restricted to AESI executives)"""
    
    if not (request.user.is_aesi_executive or request.user.is_staff):
        return render(request, 'dashboard/access_denied.html')
    
    # Get all participations with filters
    participations = Participation.objects.filter(
        otp_verified=True
    ).select_related('user', 'activity', 'activity__club')
    
    # Filter by club
    club_filter = request.GET.get('club')
    if club_filter:
        participations = participations.filter(activity__club__slug=club_filter)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        participations = participations.filter(activity__date__gte=date_from)
    if date_to:
        participations = participations.filter(activity__date__lte=date_to)
    
    clubs = Club.objects.filter(is_active=True)
    
    context = {
        'participations': participations,
        'clubs': clubs,
        'selected_club': club_filter,
    }
    
    return render(request, 'dashboard/all_participants.html', context)


# API views
@api_view(['GET'])
def global_stats_api(request):
    """API endpoint for global statistics"""
    
    cache_key = 'global_stats_api'
    data = cache.get(cache_key)
    
    if not data:
        total_clubs = Club.objects.filter(is_active=True).count()
        total_activities = Activity.objects.filter(status='COMPLETED').count()
        total_participants = Participation.objects.filter(otp_verified=True).count()
        total_users = User.objects.filter(is_active=True).count()
        
        # Average participation per activity
        avg_participation = Participation.objects.filter(
            otp_verified=True
        ).values('activity').annotate(
            count=Count('id')
        ).aggregate(avg=Avg('count'))['avg'] or 0
        
        data = {
            'total_clubs': total_clubs,
            'total_activities': total_activities,
            'total_participants': total_participants,
            'total_users': total_users,
            'average_participation_per_activity': round(avg_participation, 2),
        }
        
        cache.set(cache_key, data, 900)  # Cache for 15 minutes
    
    return Response(data)


@api_view(['GET'])
def club_stats_api(request):
    """API endpoint for club-specific statistics"""
    
    clubs = Club.objects.filter(is_active=True)
    
    club_data = []
    for club in clubs:
        activities_count = club.activities.filter(status='COMPLETED').count()
        participants_count = Participation.objects.filter(
            activity__club=club,
            otp_verified=True
        ).count()
        
        club_data.append({
            'id': club.id,
            'name': club.name,
            'slug': club.slug,
            'type': club.type,
            'execution_rate': club.execution_rate,
            'activities_count': activities_count,
            'participants_count': participants_count,
        })
    
    return Response(club_data)


@api_view(['GET'])
def participation_trends_api(request):
    """API endpoint for participation trends"""
    
    # Get data for the last 12 months
    months = request.GET.get('months', 12)
    start_date = timezone.now() - timedelta(days=30 * int(months))
    
    participations = Participation.objects.filter(
        created_at__gte=start_date,
        otp_verified=True
    )
    
    # Group by club and month
    club_trends = {}
    for club in Club.objects.filter(is_active=True):
        club_participations = participations.filter(activity__club=club)
        
        # Aggregate by month
        monthly_data = club_participations.extra(
            select={'month': "DATE_TRUNC('month', created_at)"}
        ).values('month').annotate(count=Count('id')).order_by('month')
        
        club_trends[club.name] = [
            {
                'month': item['month'].strftime('%Y-%m') if item['month'] else '',
                'count': item['count']
            }
            for item in monthly_data
        ]
    
    return Response(club_trends)


@api_view(['GET'])
def top_participants_api(request):
    """API endpoint for top participants"""
    
    limit = int(request.GET.get('limit', 10))
    club_filter = request.GET.get('club')
    
    if club_filter:
        # Top participants for specific club
        participations = Participation.objects.filter(
            activity__club__slug=club_filter,
            otp_verified=True
        ).values('user').annotate(
            count=Count('id'),
            avg_rating=Avg('rating')
        ).order_by('-count')[:limit]
        
        # Get user details
        top_users = []
        for item in participations:
            user = User.objects.get(id=item['user'])
            top_users.append({
                'id': user.id,
                'full_name': user.get_full_name(),
                'email': user.email,
                'participations_count': item['count'],
                'average_rating': round(item['avg_rating'], 2) if item['avg_rating'] else None,
            })
    else:
        # Top participants across all clubs
        stats = ParticipationStats.objects.select_related('user').order_by(
            '-total_participations'
        )[:limit]
        
        top_users = [
            {
                'id': stat.user.id,
                'full_name': stat.user.get_full_name(),
                'email': stat.user.email,
                'participations_count': stat.total_participations,
                'average_rating': round(stat.average_rating, 2),
                'total_wins': stat.total_wins,
            }
            for stat in stats
        ]
    
    return Response(top_users)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def financial_summary_api(request):
    """API endpoint for financial summary (restricted)"""
    
    # Check permissions
    if not (request.user.is_aesi_executive or request.user.is_staff):
        return Response(
            {'error': 'Permission denied'},
            status=403
        )
    
    clubs = Club.objects.filter(is_active=True)
    
    financial_data = []
    for club in clubs:
        total_income = Transaction.objects.filter(
            club=club,
            transaction_type='INCOME'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_expenses = Transaction.objects.filter(
            club=club,
            transaction_type='EXPENSE'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        balance = total_income - total_expenses
        
        financial_data.append({
            'club_id': club.id,
            'club_name': club.name,
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'balance': float(balance),
        })
    
    return Response(financial_data)

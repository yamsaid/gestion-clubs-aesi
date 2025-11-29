"""
Views for clubs app
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Club, Activity, ActionPlan, Task, Competition, ClubMember, ActivityPhoto, ActivityResource, Winner
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
    activities = club.activities.all().order_by('-date')
    
    context = {
        'club': club,
        'activities': activities,
    }
    return render(request, 'clubs/club_activities.html', context)


@login_required
def add_activity(request, slug):
    """Add a new activity to a club"""
    from .forms import ActivityForm
    
    club = get_object_or_404(Club, slug=slug)
    
    # Check permissions - only club executives, AESI executives, or staff can add activities
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas la permission d'ajouter une activité.")
        return redirect('clubs:club_activities', slug=slug)
    
    # Additional check: club executives can only add activities to their own club
    if request.user.is_club_executive and hasattr(request.user, 'club_member'):
        if request.user.club_member.club != club:
            messages.error(request, "Vous ne pouvez ajouter des activités que pour votre propre club.")
            return redirect('clubs:club_activities', slug=slug)
    
    if request.method == 'POST':
        form = ActivityForm(request.POST, request.FILES)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.club = club
            activity.created_by = request.user
            activity.save()
            
            messages.success(request, f'L\'activité "{activity.title}" a été ajoutée avec succès!')
            return redirect('clubs:club_activities', slug=slug)
        else:
            messages.error(request, "Erreur lors de l'ajout de l'activité. Veuillez vérifier les champs.")
    else:
        form = ActivityForm()
    
    context = {
        'club': club,
        'form': form,
    }
    return render(request, 'clubs/add_activity.html', context)


@login_required
def edit_activity(request, slug, activity_id):
    """Edit an existing activity"""
    from .forms import ActivityForm
    
    club = get_object_or_404(Club, slug=slug)
    activity = get_object_or_404(Activity, id=activity_id, club=club)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas la permission de modifier cette activité.")
        return redirect('clubs:club_activities', slug=slug)
    
    # Additional check for club executives
    if request.user.is_club_executive and hasattr(request.user, 'club_member'):
        if request.user.club_member.club != club:
            messages.error(request, "Vous ne pouvez modifier que les activités de votre propre club.")
            return redirect('clubs:club_activities', slug=slug)
    
    if request.method == 'POST':
        form = ActivityForm(request.POST, request.FILES, instance=activity)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.updated_by = request.user
            activity.save()
            
            messages.success(request, f'L\'activité "{activity.title}" a été modifiée avec succès!')
            return redirect('clubs:club_activities', slug=slug)
        else:
            messages.error(request, "Erreur lors de la modification de l'activité. Veuillez vérifier les champs.")
    else:
        form = ActivityForm(instance=activity)
    
    context = {
        'club': club,
        'activity': activity,
        'form': form,
    }
    return render(request, 'clubs/edit_activity.html', context)


@login_required
def delete_activity(request, slug, activity_id):
    """Delete an activity"""
    club = get_object_or_404(Club, slug=slug)
    activity = get_object_or_404(Activity, id=activity_id, club=club)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas la permission de supprimer cette activité.")
        return redirect('clubs:club_activities', slug=slug)
    
    # Additional check for club executives
    if request.user.is_club_executive and hasattr(request.user, 'club_member'):
        if request.user.club_member.club != club:
            messages.error(request, "Vous ne pouvez supprimer que les activités de votre propre club.")
            return redirect('clubs:club_activities', slug=slug)
    
    if request.method == 'POST':
        activity_title = activity.title
        activity.delete()
        messages.success(request, f'L\'activité "{activity_title}" a été supprimée avec succès!')
        return redirect('clubs:club_activities', slug=slug)
    
    context = {
        'club': club,
        'activity': activity,
    }
    return render(request, 'clubs/delete_activity.html', context)


def club_members(request, slug):
    """Club members page"""
    club = get_object_or_404(Club, slug=slug)
    members = club.members.filter(is_active=True)
    
    context = {
        'club': club,
        'members': members,
    }
    return render(request, 'clubs/club_members.html', context)


def club_bureau(request, slug):
    """Club bureau (executive team) page"""
    club = get_object_or_404(Club, slug=slug)
    members = club.members.filter(is_active=True).select_related('user').order_by('position')
    
    context = {
        'club': club,
        'members': members,
    }
    return render(request, 'clubs/club_bureau.html', context)


def club_budget(request, slug):
    """Club budget page with expense tracking"""
    from django.db.models import Sum, Count
    from finances.models import Transaction
    from django.http import HttpResponse
    import csv
    import json
    
    club = get_object_or_404(Club, slug=slug)
    
    # Get year filter from request
    year_filter = request.GET.get('year', '')
    
    # Get all activities
    activities = club.activities.all()
    
    # Base queryset for transactions
    income_qs = Transaction.objects.filter(club=club, transaction_type='INCOME')
    expense_qs = Transaction.objects.filter(club=club, transaction_type='EXPENSE')
    
    # Apply year filter if provided
    if year_filter:
        income_qs = income_qs.filter(transaction_date__year=year_filter)
        expense_qs = expense_qs.filter(transaction_date__year=year_filter)
    
    # Calculate totals
    total_income = income_qs.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = expense_qs.aggregate(total=Sum('amount'))['total'] or 0
    balance = total_income - total_expenses
    
    # Get all expenses with pagination
    from django.core.paginator import Paginator
    
    expenses_list = expense_qs.select_related('activity').order_by('-transaction_date')
    expenses_paginator = Paginator(expenses_list, 10)  # 10 expenses per page
    expenses_page_number = request.GET.get('expenses_page', 1)
    expenses = expenses_paginator.get_page(expenses_page_number)
    
    # Get available years for filter
    available_years = Transaction.objects.filter(
        club=club
    ).dates('transaction_date', 'year', order='DESC')
    
    # Export to CSV if requested
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="depenses_{club.slug}_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['#', 'Date', 'Type', 'Catégorie', 'Description', 'Montant (FCFA)', 'Activité', 'Notes'])
        
        all_transactions = Transaction.objects.filter(club=club, transaction_type='EXPENSE')
        if year_filter:
            all_transactions = all_transactions.filter(transaction_date__year=year_filter)
        all_transactions = all_transactions.select_related('activity').order_by('-transaction_date')
        
        for idx, transaction in enumerate(all_transactions, 1):
            writer.writerow([
                idx,
                transaction.transaction_date.strftime('%d/%m/%Y'),
                'Dépense',
                transaction.category,
                transaction.description,
                float(transaction.amount),
                transaction.activity.title if transaction.activity else '-',
                transaction.notes or '-'
            ])
        
        return response
    
    # Expenses by activity for statistics
    expense_by_activity = Transaction.objects.filter(
        club=club,
        transaction_type='EXPENSE',
        activity__isnull=False
    )
    if year_filter:
        expense_by_activity = expense_by_activity.filter(transaction_date__year=year_filter)
    
    expense_by_activity = expense_by_activity.values('activity__title').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Prepare data for Plotly chart
    chart_activities = [item['activity__title'] for item in expense_by_activity]
    chart_amounts = [float(item['total']) for item in expense_by_activity]
    
    expense_chart_data = json.dumps([{
        'x': chart_activities,
        'y': chart_amounts,
        'type': 'bar',
        'marker': {'color': '#FF6B35'},
        'text': [f"{amount:,.0f} FCFA" for amount in chart_amounts],
        'textposition': 'auto',
    }])
    
    context = {
        'club': club,
        'activities': activities,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'expenses': expenses,
        'expense_by_activity': expense_by_activity,
        'expense_chart_data': expense_chart_data,
        'available_years': available_years,
        'year_filter': year_filter,
    }
    return render(request, 'clubs/club_budget.html', context)


@login_required
def add_expense(request, slug):
    """Add expense to club budget"""
    from finances.models import Transaction
    from finances.forms import TransactionForm
    
    club = get_object_or_404(Club, slug=slug)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas la permission d'ajouter une dépense.")
        return redirect('clubs:club_budget', slug=slug)
    
    if request.method == 'POST':
        # Create transaction manually from form data
        activity_id = request.POST.get('activity')
        activity = Activity.objects.get(id=activity_id) if activity_id else None
        
        transaction = Transaction.objects.create(
            club=club,
            transaction_type='EXPENSE',
            amount=request.POST.get('amount'),
            description=request.POST.get('description'),
            category=request.POST.get('category'),
            transaction_date=request.POST.get('transaction_date'),
            activity=activity,
            notes=request.POST.get('notes', ''),
            created_by=request.user
        )
        
        messages.success(request, 'Dépense ajoutée avec succès!')
        return redirect('clubs:club_budget', slug=slug)
    
    return redirect('clubs:club_budget', slug=slug)


def club_programs(request, slug):
    """Club programs (action plans) page"""
    club = get_object_or_404(Club, slug=slug)
    action_plans = club.action_plans.all().prefetch_related('tasks', 'tasks__assigned_to')
    
    context = {
        'club': club,
        'action_plans': action_plans,
    }
    return render(request, 'clubs/club_programs.html', context)


def club_form_generator(request, slug):
    """Club form generator page"""
    from participation.models import DynamicParticipationForm
    from django.db.models import Q
    
    club = get_object_or_404(Club, slug=slug)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas accès au générateur de formulaires.")
        return redirect('clubs:club_detail', slug=slug)
    
    # Get only non-completed activities (planned or ongoing)
    activities = club.activities.filter(
        Q(status='PLANNED') | Q(status='ONGOING')
    ).order_by('-date')
    
    # Get active non-expired forms
    active_forms = DynamicParticipationForm.objects.filter(
        activity__club=club,
        is_active=True,
        otp_expires_at__gt=timezone.now()
    ).select_related('activity', 'created_by').order_by('-created_at')
    
    context = {
        'club': club,
        'activities': activities,
        'active_forms': active_forms,
    }
    return render(request, 'clubs/club_form_generator.html', context)


@login_required
def generate_participation_form(request, slug):
    """Generate participation form with OTP"""
    from participation.models import DynamicParticipationForm
    from core.utils import generate_otp
    from django.utils import timezone
    from datetime import timedelta
    import uuid
    
    club = get_object_or_404(Club, slug=slug)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas la permission de générer un formulaire.")
        return redirect('clubs:club_form_generator', slug=slug)
    
    if request.method == 'POST':
        activity_id = request.POST.get('activity')
        activity = get_object_or_404(Activity, id=activity_id, club=club)
        
        # Check if form already exists for this activity
        existing_form = DynamicParticipationForm.objects.filter(activity=activity).first()
        if existing_form:
            messages.warning(request, f'Un formulaire existe déjà pour cette activité. Code OTP: {existing_form.otp_code}')
            return redirect('clubs:club_form_generator', slug=slug)
        
        # Generate OTP
        otp_code = generate_otp(6)
        
        # Create form
        form_link = str(uuid.uuid4())[:8]
        expires_at = timezone.now() + timedelta(hours=3)
        
        dynamic_form = DynamicParticipationForm.objects.create(
            activity=activity,
            created_by=request.user,
            otp_code=otp_code,
            otp_expires_at=expires_at,
            form_link=form_link,
            is_active=True
        )
        
        # Store OTP in cache as well
        from core.utils import store_otp
        store_otp(activity.id, otp_code, validity_minutes=180)
        
        messages.success(request, f'Formulaire généré avec succès ! Code OTP: {otp_code}')
        return redirect('clubs:club_form_generator', slug=slug)
    
    return redirect('clubs:club_form_generator', slug=slug)


def club_dashboard(request, slug):
    """Club dashboard with analytics"""
    from django.db.models import Sum, Count, Q
    from participation.models import Participation
    from finances.models import Transaction
    from clubs.models import Winner
    import json
    
    club = get_object_or_404(Club, slug=slug)
    
    # Get all activities
    activities = club.activities.filter(status='COMPLETED')
    
    # Key Metrics
    total_participants = Participation.objects.filter(
        activity__club=club,
        otp_verified=True
    ).values('user').distinct().count()
    
    total_activities = activities.count()
    
    # Financial metrics
    total_income = Transaction.objects.filter(
        club=club,
        transaction_type='INCOME'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_expenses = Transaction.objects.filter(
        club=club,
        transaction_type='EXPENSE'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    balance = total_income - total_expenses
    
    # Participants by Activity Chart (Bar Chart)
    participants_by_activity = Participation.objects.filter(
        activity__club=club,
        otp_verified=True
    ).values('activity__title').annotate(
        count=Count('id')
    ).order_by('-count')
    
    activity_names = [item['activity__title'] for item in participants_by_activity]
    participant_counts = [item['count'] for item in participants_by_activity]
    
    participants_by_activity_data = json.dumps([{
        'x': activity_names,
        'y': participant_counts,
        'type': 'bar',
        'marker': {'color': '#3B82F6'},
        'text': participant_counts,
        'textposition': 'auto',
    }])
    
    # TOP 10 Participants
    top_participants_data = Participation.objects.filter(
        activity__club=club,
        otp_verified=True
    ).values('user').annotate(
        participation_count=Count('id')
    ).order_by('-participation_count')[:10]
    
    top_10_participants = []
    for item in top_participants_data:
        from users.models import User
        user = User.objects.get(id=item['user'])
        attendance_percentage = round((item['participation_count'] / total_activities * 100), 2) if total_activities > 0 else 0
        top_10_participants.append({
            'user': user,
            'participation_count': item['participation_count'],
            'attendance_percentage': attendance_percentage
        })
    
    # Winners
    winners = Winner.objects.filter(
        competition__activity__club=club
    ).select_related('participant', 'competition')[:10]
    
    # Detailed Analysis Data (by gender, filiere, niveau)
    analysis_data = {'all': {'gender': {}, 'filiere': {}, 'niveau': {}}}
    
    # Overall analysis
    all_participations = Participation.objects.filter(
        activity__club=club,
        otp_verified=True
    ).select_related('user')
    
    for p in all_participations:
        # Gender
        gender = p.user.gender or 'Non spécifié'
        analysis_data['all']['gender'][gender] = analysis_data['all']['gender'].get(gender, 0) + 1
        
        # Filiere
        filiere = p.user.get_filiere_display() or 'Non spécifié'
        analysis_data['all']['filiere'][filiere] = analysis_data['all']['filiere'].get(filiere, 0) + 1
        
        # Niveau
        niveau = p.user.niveau or 'Non spécifié'
        analysis_data['all']['niveau'][niveau] = analysis_data['all']['niveau'].get(niveau, 0) + 1
    
    # Per activity analysis
    for activity in activities:
        activity_participations = Participation.objects.filter(
            activity=activity,
            otp_verified=True
        ).select_related('user')
        
        analysis_data[str(activity.id)] = {'gender': {}, 'filiere': {}, 'niveau': {}}
        
        for p in activity_participations:
            gender = p.user.gender or 'Non spécifié'
            analysis_data[str(activity.id)]['gender'][gender] = analysis_data[str(activity.id)]['gender'].get(gender, 0) + 1
            
            filiere = p.user.get_filiere_display() or 'Non spécifié'
            analysis_data[str(activity.id)]['filiere'][filiere] = analysis_data[str(activity.id)]['filiere'].get(filiere, 0) + 1
            
            niveau = p.user.niveau or 'Non spécifié'
            analysis_data[str(activity.id)]['niveau'][niveau] = analysis_data[str(activity.id)]['niveau'].get(niveau, 0) + 1
    
    # Expense Evolution Data
    expense_by_activity = Transaction.objects.filter(
        club=club,
        transaction_type='EXPENSE',
        activity__isnull=False
    ).values('activity__title').annotate(
        total=Sum('amount')
    ).order_by('activity__date')
    
    expense_activities = [item['activity__title'] for item in expense_by_activity]
    expense_amounts = [float(item['total']) for item in expense_by_activity]
    
    expense_evolution_data = json.dumps([{
        'x': expense_activities,
        'y': expense_amounts,
        'type': 'scatter',
        'mode': 'lines+markers',
        'line': {'color': '#EF4444', 'width': 3},
        'marker': {'size': 8, 'color': '#DC2626'},
        'fill': 'tozeroy',
        'fillcolor': 'rgba(239, 68, 68, 0.1)',
    }])
    
    # Action Plans
    action_plans = club.action_plans.all().prefetch_related('tasks')
    
    context = {
        'club': club,
        'activities': activities,
        'total_participants': total_participants,
        'total_activities': total_activities,
        'balance': balance,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'participants_by_activity_data': participants_by_activity_data,
        'top_10_participants': top_10_participants,
        'winners': winners,
        'analysis_data': json.dumps(analysis_data),
        'expense_evolution_data': expense_evolution_data,
        'action_plans': action_plans,
    }
    return render(request, 'clubs/club_dashboard.html', context)


def club_participants(request, slug):
    """Club participants page with 3 tables"""
    from django.core.paginator import Paginator
    from django.db.models import Count, Q
    from participation.models import Participation
    from clubs.models import Winner
    from django.http import HttpResponse
    import csv
    
    club = get_object_or_404(Club, slug=slug)
    
    # Get year filter from request
    year_filter = request.GET.get('year', '')
    
    # Get all activities for this club
    activities = club.activities.filter(status='COMPLETED')
    if year_filter:
        activities = activities.filter(date__year=year_filter)
    
    # Base queryset for participations
    base_participations = Participation.objects.filter(
        activity__club=club,
        otp_verified=True
    )
    if year_filter:
        base_participations = base_participations.filter(activity__date__year=year_filter)
    
    # Get available years for filter
    available_years = Participation.objects.filter(
        activity__club=club,
        otp_verified=True
    ).dates('activity__date', 'year', order='DESC')
    
    # Export to CSV if requested
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="participants_{club.slug}_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['#', 'Nom', 'Prénom', 'Email', 'Filière', 'Niveau', 'Sexe', 'Téléphone', 'Activité', 'Date activité', 'Note', 'Date de participation'])
        
        export_participations = base_participations.select_related('user', 'activity').order_by('-created_at')
        
        for idx, participation in enumerate(export_participations, 1):
            writer.writerow([
                idx,
                participation.user.last_name,
                participation.user.first_name,
                participation.user.email,
                participation.user.get_filiere_display() or '-',
                participation.user.get_niveau_display() or '-',
                participation.user.get_gender_display() or '-',
                participation.user.phone or '-',
                participation.activity.title,
                participation.activity.date.strftime('%d/%m/%Y') if participation.activity.date else '-',
                participation.rating or '-',
                participation.submitted_at.strftime('%d/%m/%Y %H:%M') if participation.submitted_at else '-'
            ])
        
        return response
    
    # Table 1: TOP 10 participants by attendance rate
    top_participants_data = base_participations.values('user').annotate(
        participation_count=Count('id')
    ).order_by('-participation_count')[:10]
    
    # Calculate attendance percentage for top participants
    top_participants = []
    total_activities = activities.count()
    for item in top_participants_data:
        from users.models import User
        user = User.objects.get(id=item['user'])
        attendance_percentage = round((item['participation_count'] / total_activities * 100), 2) if total_activities > 0 else 0
        top_participants.append({
            'user': user,
            'participation_count': item['participation_count'],
            'attendance_percentage': attendance_percentage
        })
    
    # Table 2: Competition winners with pagination
    winners_list = Winner.objects.filter(
        competition__activity__club=club
    ).select_related('participant', 'competition', 'competition__activity').order_by('rank')
    if year_filter:
        winners_list = winners_list.filter(competition__activity__date__year=year_filter)
    
    # Pagination for winners
    winners_paginator = Paginator(winners_list, 10)  # 10 winners per page
    winners_page_number = request.GET.get('winners_page', 1)
    winners = winners_paginator.get_page(winners_page_number)
    
    # Table 3: All participants with pagination
    all_participants = base_participations.select_related('user', 'activity').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(all_participants, 10)  # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'club': club,
        'activities': activities,
        'top_participants': top_participants,
        'winners': winners,
        'all_participants': all_participants,
        'page_obj': page_obj,
        'available_years': available_years,
        'year_filter': year_filter,
    }
    return render(request, 'clubs/club_participants.html', context)


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
    resources = activity.resources.all()
    competitions = activity.competitions.all()
    
    context = {
        'activity': activity,
        'photos': photos,
        'resources': resources,
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


@login_required
def complete_activity(request, slug, activity_id):
    """Mark an activity as completed and add completion details"""
    from .forms import CompleteActivityForm, ActivityPhotoForm, ActivityResourceForm, CompetitionForm
    
    club = get_object_or_404(Club, slug=slug)
    activity = get_object_or_404(Activity, id=activity_id, club=club)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas la permission de marquer cette activité comme terminée.")
        return redirect('clubs:activity_detail', pk=activity_id)
    
    # Check if activity can be completed (must be PLANNED or ONGOING)
    if activity.status not in ['PLANNED', 'ONGOING']:
        messages.error(request, f"Cette activité est déjà {activity.get_status_display().lower()}.")
        return redirect('clubs:activity_detail', pk=activity_id)
    
    if request.method == 'POST':
        form = CompleteActivityForm(request.POST, instance=activity)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.status = 'COMPLETED'
            activity.completion_date = timezone.now()
            activity.updated_by = request.user
            activity.save()
            
            messages.success(request, f'L\'activité "{activity.title}" a été marquée comme terminée!')
            return redirect('clubs:activity_completion_details', slug=slug, activity_id=activity_id)
    else:
        form = CompleteActivityForm(instance=activity)
    
    context = {
        'club': club,
        'activity': activity,
        'form': form,
    }
    return render(request, 'clubs/complete_activity.html', context)


@login_required
def cancel_activity(request, slug, activity_id):
    """Cancel an activity with a comment"""
    from .forms import CancelActivityForm
    
    club = get_object_or_404(Club, slug=slug)
    activity = get_object_or_404(Activity, id=activity_id, club=club)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas la permission d'annuler cette activité.")
        return redirect('clubs:activity_detail', pk=activity_id)
    
    # Check if activity can be cancelled (must be PLANNED or ONGOING)
    if activity.status not in ['PLANNED', 'ONGOING']:
        messages.error(request, f"Cette activité est déjà {activity.get_status_display().lower()}.")
        return redirect('clubs:activity_detail', pk=activity_id)
    
    if request.method == 'POST':
        form = CancelActivityForm(request.POST, instance=activity)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.status = 'CANCELLED'
            activity.cancellation_date = timezone.now()
            activity.updated_by = request.user
            activity.save()
            
            messages.success(request, f'L\'activité "{activity.title}" a été annulée.')
            return redirect('clubs:club_activities', slug=slug)
    else:
        form = CancelActivityForm(instance=activity)
    
    context = {
        'club': club,
        'activity': activity,
        'form': form,
    }
    return render(request, 'clubs/cancel_activity.html', context)


@login_required
def activity_completion_details(request, slug, activity_id):
    """Add photos, resources, and competition winners to a completed activity"""
    from .forms import ActivityPhotoForm, ActivityResourceForm, CompetitionForm
    
    club = get_object_or_404(Club, slug=slug)
    activity = get_object_or_404(Activity, id=activity_id, club=club)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas la permission d'accéder à cette page.")
        return redirect('clubs:activity_detail', pk=activity_id)
    
    # Check if activity is completed
    if activity.status != 'COMPLETED':
        messages.error(request, "Cette activité n'est pas encore terminée.")
        return redirect('clubs:activity_detail', pk=activity_id)
    
    photo_form = ActivityPhotoForm()
    resource_form = ActivityResourceForm()
    competition_form = CompetitionForm()
    
    # Get existing data
    photos = activity.photos.all()
    resources = activity.resources.all()
    competitions = activity.competitions.prefetch_related('winners__participant').all()
    
    context = {
        'club': club,
        'activity': activity,
        'photo_form': photo_form,
        'resource_form': resource_form,
        'competition_form': competition_form,
        'photos': photos,
        'resources': resources,
        'competitions': competitions,
    }
    return render(request, 'clubs/activity_completion_details.html', context)


@login_required
@require_http_methods(["POST"])
def add_activity_photo(request, slug, activity_id):
    """Add a photo to an activity (AJAX)"""
    from .forms import ActivityPhotoForm
    
    club = get_object_or_404(Club, slug=slug)
    activity = get_object_or_404(Activity, id=activity_id, club=club)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Permission refusée.")
        return redirect('clubs:activity_completion_details', slug=slug, activity_id=activity_id)
    
    form = ActivityPhotoForm(request.POST, request.FILES)
    if form.is_valid():
        photo = form.save(commit=False)
        photo.activity = activity
        photo.uploaded_by = request.user
        photo.save()
        messages.success(request, 'Photo ajoutée avec succès!')
    else:
        messages.error(request, 'Erreur lors de l\'ajout de la photo.')
    
    return redirect('clubs:activity_completion_details', slug=slug, activity_id=activity_id)


@login_required
@require_http_methods(["POST"])
def add_activity_resource(request, slug, activity_id):
    """Add a resource to an activity"""
    from .forms import ActivityResourceForm
    
    club = get_object_or_404(Club, slug=slug)
    activity = get_object_or_404(Activity, id=activity_id, club=club)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Permission refusée.")
        return redirect('clubs:activity_completion_details', slug=slug, activity_id=activity_id)
    
    form = ActivityResourceForm(request.POST, request.FILES)
    if form.is_valid():
        resource = form.save(commit=False)
        resource.activity = activity
        resource.uploaded_by = request.user
        resource.save()
        messages.success(request, 'Ressource ajoutée avec succès!')
    else:
        messages.error(request, 'Erreur lors de l\'ajout de la ressource.')
    
    return redirect('clubs:activity_completion_details', slug=slug, activity_id=activity_id)


@login_required
@require_http_methods(["POST"])
def add_competition(request, slug, activity_id):
    """Add a competition to an activity"""
    from .forms import CompetitionForm
    
    club = get_object_or_404(Club, slug=slug)
    activity = get_object_or_404(Activity, id=activity_id, club=club)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Permission refusée.")
        return redirect('clubs:activity_completion_details', slug=slug, activity_id=activity_id)
    
    form = CompetitionForm(request.POST)
    if form.is_valid():
        competition = form.save(commit=False)
        competition.activity = activity
        competition.created_by = request.user
        competition.save()
        messages.success(request, f'Compétition "{competition.name}" créée avec succès!')
    else:
        messages.error(request, 'Erreur lors de la création de la compétition.')
    
    return redirect('clubs:activity_completion_details', slug=slug, activity_id=activity_id)


@login_required
def add_winner(request, slug, activity_id, competition_id):
    """Add a winner to a competition"""
    from .forms import WinnerForm
    from participation.models import Participation
    
    club = get_object_or_404(Club, slug=slug)
    activity = get_object_or_404(Activity, id=activity_id, club=club)
    competition = get_object_or_404(Competition, id=competition_id, activity=activity)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Permission refusée.")
        return redirect('clubs:activity_completion_details', slug=slug, activity_id=activity_id)
    
    if request.method == 'POST':
        form = WinnerForm(request.POST)
        if form.is_valid():
            winner = form.save(commit=False)
            winner.competition = competition
            winner.save()
            messages.success(request, f'Gagnant ajouté: {winner.participant.get_full_name()} - Rang {winner.rank}')
            return redirect('clubs:activity_completion_details', slug=slug, activity_id=activity_id)
    else:
        # Get participants of this activity for the dropdown
        participants = Participation.objects.filter(
            activity=activity,
            otp_verified=True
        ).select_related('user').values_list('user', flat=True)
        
        form = WinnerForm()
        # Filter participant choices to only show activity participants
        from users.models import User
        form.fields['participant'].queryset = User.objects.filter(id__in=participants)
    
    context = {
        'club': club,
        'activity': activity,
        'competition': competition,
        'form': form,
    }
    return render(request, 'clubs/add_winner.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_task_completion(request, task_id):
    """Toggle task completion status (AJAX endpoint)"""
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    task = get_object_or_404(Task, id=task_id)
    
    try:
        data = json.loads(request.body)
        is_completed = data.get('is_completed', False)
        
        task.is_completed = is_completed
        if is_completed:
            task.completed_at = timezone.now()
        else:
            task.completed_at = None
        
        task.updated_by = request.user
        task.save()
        
        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'is_completed': task.is_completed,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


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

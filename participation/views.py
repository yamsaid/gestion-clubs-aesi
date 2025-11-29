"""
Views for participation app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from clubs.models import Activity
from core.utils import generate_otp, store_otp, verify_otp, get_otp_expiry
from .models import Participation
from .serializers import ParticipationSerializer
from .forms import ParticipationForm


# Template views
@login_required
def generate_otp_view(request, activity_id):
    """Generate OTP for an activity (club executives only)"""
    activity = get_object_or_404(Activity, id=activity_id)
    
    # Check if user has permission (club executive or AESI executive)
    if not (request.user.is_club_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas la permission de générer un code OTP.")
        return redirect('clubs:activity_detail', pk=activity_id)
    
    # Generate OTP
    otp_code = generate_otp()
    expiry_time = store_otp(activity_id, otp_code)
    
    context = {
        'activity': activity,
        'otp_code': otp_code,
        'expiry_time': expiry_time,
    }
    
    return render(request, 'participation/otp_generated.html', context)


def verify_otp_view(request, activity_id):
    """Verify OTP and allow access to participation form"""
    activity = get_object_or_404(Activity, id=activity_id)
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        
        is_valid, message = verify_otp(activity_id, otp_code)
        
        if is_valid:
            # Store in session that OTP is verified
            request.session[f'otp_verified_{activity_id}'] = True
            return redirect('participation:participation_form', activity_id=activity_id)
        else:
            messages.error(request, message)
    
    expiry_time = get_otp_expiry(activity_id)
    
    context = {
        'activity': activity,
        'expiry_time': expiry_time,
    }
    
    return render(request, 'participation/verify_otp.html', context)


@login_required
def participation_form(request, activity_id):
    """Participation form (requires OTP verification)"""
    activity = get_object_or_404(Activity, id=activity_id)
    
    # Check if OTP is verified
    if not request.session.get(f'otp_verified_{activity_id}', False):
        messages.error(request, "Veuillez d'abord vérifier le code OTP.")
        return redirect('participation:verify_otp', activity_id=activity_id)
    
    # Check if user already participated
    participation, created = Participation.objects.get_or_create(
        activity=activity,
        user=request.user
    )
    
    if not created and participation.submitted_at:
        messages.info(request, "Vous avez déjà soumis votre participation pour cette activité.")
        return redirect('clubs:activity_detail', pk=activity_id)
    
    context = {
        'activity': activity,
        'participation': participation,
    }
    
    return render(request, 'participation/participation_form.html', context)


@login_required
def submit_participation(request, activity_id):
    """Submit participation form"""
    activity = get_object_or_404(Activity, id=activity_id)
    
    # Check if OTP is verified
    if not request.session.get(f'otp_verified_{activity_id}', False):
        messages.error(request, "Veuillez d'abord vérifier le code OTP.")
        return redirect('participation:verify_otp', activity_id=activity_id)
    
    participation = get_object_or_404(
        Participation,
        activity=activity,
        user=request.user
    )
    
    if request.method == 'POST':
        form = ParticipationForm(request.POST, request.FILES, instance=participation)
        if form.is_valid():
            participation = form.save(commit=False)
            participation.otp_verified = True
            participation.otp_verified_at = timezone.now()
            participation.submitted_at = timezone.now()
            participation.save()
            
            # Clear OTP verification from session
            del request.session[f'otp_verified_{activity_id}']
            
            messages.success(request, "Votre participation a été enregistrée avec succès!")
            return redirect('clubs:activity_detail', pk=activity_id)
    else:
        form = ParticipationForm(instance=participation)
    
    context = {
        'activity': activity,
        'form': form,
    }
    
    return render(request, 'participation/submit_participation.html', context)


@login_required
def participant_list(request, activity_id):
    """List of participants for an activity"""
    import csv
    from django.http import HttpResponse
    
    activity = get_object_or_404(Activity, id=activity_id)
    
    # Get year filter from request
    year_filter = request.GET.get('year', '')
    
    # Base queryset
    participants = Participation.objects.filter(
        activity=activity,
        otp_verified=True
    ).select_related('user')
    
    # Apply year filter if provided
    if year_filter:
        participants = participants.filter(activity__date__year=year_filter)
    
    # Get available years for filter
    available_years = Participation.objects.filter(
        activity__club=activity.club,
        otp_verified=True
    ).dates('activity__date', 'year', order='DESC')
    
    # Export to CSV if requested
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="participants_{activity.title}_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['#', 'Nom', 'Prénom', 'Email', 'Filière', 'Niveau', 'Sexe', 'Téléphone', 'Note', 'Date de participation'])
        
        for idx, participation in enumerate(participants, 1):
            writer.writerow([
                idx,
                participation.user.last_name,
                participation.user.first_name,
                participation.user.email,
                participation.user.get_filiere_display() or '-',
                participation.user.get_niveau_display() or '-',
                participation.user.get_gender_display() or '-',
                participation.user.phone or '-',
                participation.rating or '-',
                participation.submitted_at.strftime('%d/%m/%Y %H:%M') if participation.submitted_at else '-'
            ])
        
        return response
    
    context = {
        'activity': activity,
        'participants': participants,
        'available_years': available_years,
        'year_filter': year_filter,
    }
    
    return render(request, 'participation/participant_list.html', context)


# API views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_otp_api(request, activity_id):
    """API endpoint to generate OTP"""
    activity = get_object_or_404(Activity, id=activity_id)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_staff):
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    otp_code = generate_otp()
    expiry_time = store_otp(activity_id, otp_code)
    
    return Response({
        'otp_code': otp_code,
        'expiry_time': expiry_time.isoformat(),
        'activity': activity.title
    })


@api_view(['POST'])
def verify_otp_api(request):
    """API endpoint to verify OTP"""
    activity_id = request.data.get('activity_id')
    otp_code = request.data.get('otp_code')
    
    if not activity_id or not otp_code:
        return Response(
            {'error': 'activity_id and otp_code are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    activity = get_object_or_404(Activity, id=activity_id)
    is_valid, message = verify_otp(activity_id, otp_code)
    
    if is_valid:
        return Response({
            'valid': True,
            'message': message,
            'activity': activity.title
        })
    else:
        return Response({
            'valid': False,
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)


class ParticipationViewSet(viewsets.ModelViewSet):
    """ViewSet for Participation model"""
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Participation.objects.all()
        
        # Filter by activity
        activity_id = self.request.query_params.get('activity', None)
        if activity_id:
            queryset = queryset.filter(activity_id=activity_id)
        
        # Filter by club
        club_id = self.request.query_params.get('club', None)
        if club_id:
            queryset = queryset.filter(activity__club_id=club_id)
        
        # Only show verified participations for non-executives
        if not (self.request.user.is_club_executive or 
                self.
                self.request.user.is_staff):
            queryset = queryset.filter(otp_verified=True)
        
        return queryset


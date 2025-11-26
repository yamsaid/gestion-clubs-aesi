"""
Views for users app
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import UserProfileForm
from .models import User


@login_required
def profile(request):
    """
    User profile page
    """
    from participation.models import Participation
    
    participations = Participation.objects.filter(
        user=request.user,
        otp_verified=True
    ).select_related('activity', 'activity__club').order_by('-created_at')[:10]
    
    context = {
        'user': request.user,
        'participations': participations,
    }
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile(request):
    """
    Edit user profile
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    """
    Change user password
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep user logged in
            messages.success(request, 'Votre mot de passe a été changé avec succès.')
            return redirect('users:profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})


def custom_signup(request):
    """
    Custom signup view - redirects to allauth signup
    Note: This view is kept for URL compatibility but allauth handles the actual signup
    """
    return redirect('account_signup')

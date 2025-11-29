"""
Core views
"""
from django.shortcuts import render
from clubs.models import Club


def home(request):
    """
    Home page with overview of all clubs
    """
    clubs = Club.objects.all()
    context = {
        'clubs': clubs,
    }
    return render(request, 'core/home.html', context)


def about(request):
    """
    About AESI page
    """
    return render(request, 'core/about.html')


def user_guide(request):
    """
    User guide page
    """
    return render(request, 'core/user_guide.html')

"""
Template tags for permission checks
"""
from django import template

register = template.Library()


@register.simple_tag
def can_manage_club(user, club):
    """Check if user can manage a specific club"""
    if not user.is_authenticated:
        return False
    return user.can_manage_club(club)


@register.simple_tag
def can_view_finances(user, club=None):
    """Check if user can view financial data"""
    if not user.is_authenticated:
        return False
    return user.can_view_finances(club)


@register.simple_tag
def can_modify_finances(user, club=None):
    """Check if user can modify financial data"""
    if not user.is_authenticated:
        return False
    return user.can_modify_finances(club)


@register.filter
def is_student(user):
    """Check if user is a student"""
    return user.is_authenticated and user.is_student


@register.filter
def is_club_executive(user):
    """Check if user is a club executive"""
    return user.is_authenticated and user.is_club_executive


@register.filter
def is_aesi_treasurer(user):
    """Check if user is AESI treasurer"""
    return user.is_authenticated and user.is_aesi_treasurer




@register.simple_tag
def get_user_club(user):
    """Get the club the user belongs to"""
    if not user.is_authenticated:
        return None
    return user.get_user_club()


@register.simple_tag
def user_role_display(user):
    """Get user role display name"""
    if not user.is_authenticated:
        return "Non connecté"
    return user.get_role_display()

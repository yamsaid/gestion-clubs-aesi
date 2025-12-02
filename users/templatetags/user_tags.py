"""
Custom template tags for user permissions
"""
from django import template

register = template.Library()


@register.filter
def can_view_finances(user, club=None):
    """Check if user can view finances for a club"""
    if not user.is_authenticated:
        return False
    return user.can_view_finances(club)


@register.filter
def can_modify_finances(user, club=None):
    """Check if user can modify finances for a club"""
    if not user.is_authenticated:
        return False
    return user.can_modify_finances(club)


@register.filter
def can_manage_club(user, club):
    """Check if user can manage a club"""
    if not user.is_authenticated:
        return False
    return user.can_manage_club(club)

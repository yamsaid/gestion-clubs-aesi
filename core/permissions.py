"""
Custom permissions for AESI platform
"""
from rest_framework import permissions


class IsClubExecutive(permissions.BasePermission):
    """
    Permission to check if user is an executive member of a club
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'club_member')

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for club executives
        return hasattr(request.user, 'club_member') and request.user.club_member.club == obj


class IsAESIExecutive(permissions.BasePermission):
    """
    Permission to check if user is an AESI executive member
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == 'AESI_EXECUTIVE'
        )


class IsClubExecutiveOrAESI(permissions.BasePermission):
    """
    Permission to check if user is either a club executive or AESI executive
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return (
            request.user.role in ['CLUB_EXECUTIVE', 'AESI_EXECUTIVE'] or
            request.user.is_staff
        )


class CanViewFinancialData(permissions.BasePermission):
    """
    Permission to view financial data - restricted to executives only
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.role in ['CLUB_EXECUTIVE', 'AESI_EXECUTIVE'] or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # AESI executives can view all financial data
        if request.user.role == 'AESI_EXECUTIVE' or request.user.is_staff:
            return True
        
        # Club executives can only view their club's financial data
        if request.user.role == 'CLUB_EXECUTIVE':
            club = getattr(obj, 'club', None)
            return hasattr(request.user, 'club_member') and request.user.club_member.club == club
        
        return False

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
    Permission to view financial data
    
    Rules:
    - Étudiant: NO
    - Membre exécutif du club: Only their club
    - Trésorier AESI: ALL clubs (read-only)
    - Staff: ALL clubs
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Students cannot view finances
        if request.user.is_student:
            return False
        
        # Club executives, treasurers, and staff can view
        return request.user.role in ['CLUB_EXECUTIVE', 'AESI_TREASURER'] or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        club = getattr(obj, 'club', None)
        return request.user.can_view_finances(club)


class CanModifyFinancialData(permissions.BasePermission):
    """
    Permission to modify financial data
    
    Rules:
    - Étudiant: NO
    - Membre exécutif du club: Only their club
    - Trésorier AESI: NO (read-only)
    - Staff: ALL clubs
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Students and treasurers cannot modify
        if request.user.is_student or request.user.is_aesi_treasurer:
            return False
        
        # Club executives and staff can modify
        return request.user.is_club_executive or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        club = getattr(obj, 'club', None)
        return request.user.can_modify_finances(club)

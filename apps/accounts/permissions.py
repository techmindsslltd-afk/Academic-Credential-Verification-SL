"""
Custom permissions for role-based access control
"""
from rest_framework import permissions
from .models import UserRole


class IsSuperAdmin(permissions.BasePermission):
    """Allow access only to super admins"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.SUPER_ADMIN
        )


class IsInstitutionAdmin(permissions.BasePermission):
    """Allow access only to institution admins"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.INSTITUTION_ADMIN
        )


class IsStudent(permissions.BasePermission):
    """Allow access only to students"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.STUDENT
        )


class IsEmployer(permissions.BasePermission):
    """Allow access only to employers"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.EMPLOYER
        )


class IsSuperAdminOrInstitutionAdmin(permissions.BasePermission):
    """Allow access to super admins and institution admins"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in [UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN]
        )


class IsOwnerOrSuperAdmin(permissions.BasePermission):
    """Allow access to the owner of the object or super admin"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.SUPER_ADMIN:
            return True
        
        # Check if the object has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return obj == request.user


class CanIssueCredentials(permissions.BasePermission):
    """Check if user can issue credentials"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == UserRole.SUPER_ADMIN:
            return True
        
        if request.user.role == UserRole.INSTITUTION_ADMIN:
            try:
                profile = request.user.institution_admin_profile
                return profile.can_issue_credentials
            except:
                return False
        
        return False


class CanRevokeCredentials(permissions.BasePermission):
    """Check if user can revoke credentials"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == UserRole.SUPER_ADMIN:
            return True
        
        if request.user.role == UserRole.INSTITUTION_ADMIN:
            try:
                profile = request.user.institution_admin_profile
                return profile.can_revoke_credentials
            except:
                return False
        
        return False


class CanVerifyCredentials(permissions.BasePermission):
    """Check if user can verify credentials"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super admin and institution admin can always verify
        if request.user.role in [UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN]:
            return True
        
        # Employers can verify within their quota
        if request.user.role == UserRole.EMPLOYER:
            try:
                profile = request.user.employer_profile
                return profile.verifications_this_month < profile.monthly_verification_limit
            except:
                return False
        
        return False

"""
Django admin configuration for accounts
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, StudentProfile, InstitutionAdminProfile,
    EmployerProfile, EmailVerificationToken, PasswordResetToken, ActivityLog
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'role', 'is_active', 'is_verified', 'date_joined']
    list_filter = ['role', 'is_active', 'is_verified', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_verified', 'email_verified')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'institution', 'program', 'graduation_date']
    list_filter = ['institution']
    search_fields = ['user__email', 'student_id']


@admin.register(InstitutionAdminProfile)
class InstitutionAdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'institution', 'department', 'position']
    list_filter = ['institution']


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'industry', 'api_enabled']
    list_filter = ['industry', 'api_enabled']
    search_fields = ['company_name', 'user__email']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['user', 'action', 'description', 'ip_address', 'user_agent', 'metadata', 'created_at']

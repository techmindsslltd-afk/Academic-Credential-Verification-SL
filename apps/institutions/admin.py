"""
Django admin for institutions
"""
from django.contrib import admin
from .models import Institution, Program, AccreditationRecord


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution_type', 'country', 'accreditation_status', 'is_partner', 'is_verified']
    list_filter = ['institution_type', 'accreditation_status', 'country', 'is_partner', 'is_verified']
    search_fields = ['name', 'whed_id', 'city']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution', 'degree_level', 'department', 'is_active']
    list_filter = ['degree_level', 'is_active']
    search_fields = ['name', 'code', 'institution__name']


@admin.register(AccreditationRecord)
class AccreditationRecordAdmin(admin.ModelAdmin):
    list_display = ['institution', 'accreditation_body', 'status', 'granted_date', 'expiry_date']
    list_filter = ['status', 'accreditation_body']
    search_fields = ['institution__name']

"""
Django admin for accreditation
"""
from django.contrib import admin
from .models import AccreditationBody, WHEDRecord, AccreditationLookupLog


@admin.register(AccreditationBody)
class AccreditationBodyAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'body_type', 'is_recognized']
    list_filter = ['body_type', 'country', 'is_recognized']
    search_fields = ['name', 'short_name']


@admin.register(WHEDRecord)
class WHEDRecordAdmin(admin.ModelAdmin):
    list_display = ['institution_name', 'whed_id', 'country', 'is_accredited']
    list_filter = ['country', 'is_accredited']
    search_fields = ['institution_name', 'whed_id', 'city']


@admin.register(AccreditationLookupLog)
class AccreditationLookupLogAdmin(admin.ModelAdmin):
    list_display = ['search_query', 'search_type', 'results_count', 'user', 'created_at']
    list_filter = ['search_type']
    date_hierarchy = 'created_at'

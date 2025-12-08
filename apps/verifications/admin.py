"""
Django admin for verifications
"""
from django.contrib import admin
from .models import VerificationLog, VerificationReport, FraudAlert


@admin.register(VerificationLog)
class VerificationLogAdmin(admin.ModelAdmin):
    list_display = ['credential_id_searched', 'result', 'method', 'verifier', 'created_at']
    list_filter = ['result', 'method', 'created_at']
    search_fields = ['credential_id_searched', 'verifier__email']
    date_hierarchy = 'created_at'


@admin.register(VerificationReport)
class VerificationReportAdmin(admin.ModelAdmin):
    list_display = ['report_date', 'total_verifications', 'valid_verifications', 'invalid_verifications']
    date_hierarchy = 'report_date'


@admin.register(FraudAlert)
class FraudAlertAdmin(admin.ModelAdmin):
    list_display = ['alert_type', 'severity', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'severity', 'is_resolved']

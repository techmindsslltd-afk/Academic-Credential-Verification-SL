"""
Django admin for credentials
"""
from django.contrib import admin
from .models import Credential, CredentialShare, CredentialBatch, BlockchainTransaction


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = ['credential_id', 'holder_name', 'institution', 'credential_type', 'status', 'issue_date']
    list_filter = ['status', 'credential_type', 'institution']
    search_fields = ['credential_id', 'holder_name', 'holder__email']
    readonly_fields = ['credential_id', 'blockchain_hash', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(CredentialShare)
class CredentialShareAdmin(admin.ModelAdmin):
    list_display = ['credential', 'shared_with_email', 'is_active', 'view_count', 'expires_at']
    list_filter = ['is_active']


@admin.register(CredentialBatch)
class CredentialBatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution', 'status', 'total_count', 'processed_count', 'created_at']
    list_filter = ['status', 'institution']


@admin.register(BlockchainTransaction)
class BlockchainTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_hash', 'credential', 'transaction_type', 'is_confirmed', 'created_at']
    list_filter = ['transaction_type', 'is_confirmed']

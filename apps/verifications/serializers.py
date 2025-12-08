"""
Serializers for verifications
"""
from rest_framework import serializers
from .models import VerificationLog, VerificationReport, FraudAlert


class VerificationLogSerializer(serializers.ModelSerializer):
    """Serializer for verification logs"""
    credential_id = serializers.CharField(source='credential.credential_id', read_only=True)
    verifier_name = serializers.CharField(source='verifier.full_name', read_only=True)
    
    class Meta:
        model = VerificationLog
        fields = [
            'id', 'credential', 'credential_id', 'credential_id_searched',
            'verifier', 'verifier_name', 'verifier_company', 'verifier_email',
            'method', 'result', 'ip_address', 'country',
            'response_time_ms', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class VerificationReportSerializer(serializers.ModelSerializer):
    """Serializer for verification reports"""
    
    class Meta:
        model = VerificationReport
        fields = [
            'id', 'report_date', 'total_verifications', 'valid_verifications',
            'invalid_verifications', 'revoked_verifications', 'not_found_verifications',
            'by_credential_id', 'by_blockchain_hash', 'by_qr_code',
            'by_share_link', 'by_api', 'avg_response_time_ms',
            'top_verifiers', 'top_credentials', 'created_at'
        ]


class FraudAlertSerializer(serializers.ModelSerializer):
    """Serializer for fraud alerts"""
    credential_id = serializers.CharField(source='credential.credential_id', read_only=True)
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.full_name', read_only=True)
    
    class Meta:
        model = FraudAlert
        fields = [
            'id', 'alert_type', 'severity', 'credential', 'credential_id',
            'institution', 'institution_name', 'description', 'ip_address',
            'metadata', 'is_resolved', 'resolved_by', 'resolved_by_name',
            'resolved_at', 'resolution_notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class VerificationStatsSerializer(serializers.Serializer):
    """Serializer for verification statistics"""
    total_verifications = serializers.IntegerField()
    valid_count = serializers.IntegerField()
    invalid_count = serializers.IntegerField()
    revoked_count = serializers.IntegerField()
    today_count = serializers.IntegerField()
    this_month_count = serializers.IntegerField()

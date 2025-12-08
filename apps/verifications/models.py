"""
Verification tracking models
"""
import uuid
from django.db import models
from django.utils import timezone


class VerificationMethod(models.TextChoices):
    CREDENTIAL_ID = 'credential_id', 'Credential ID'
    BLOCKCHAIN_HASH = 'blockchain_hash', 'Blockchain Hash'
    QR_CODE = 'qr_code', 'QR Code Scan'
    SHARE_LINK = 'share_link', 'Share Link'
    API = 'api', 'API Request'


class VerificationResult(models.TextChoices):
    VALID = 'valid', 'Valid'
    INVALID = 'invalid', 'Invalid'
    REVOKED = 'revoked', 'Revoked'
    EXPIRED = 'expired', 'Expired'
    NOT_FOUND = 'not_found', 'Not Found'
    ERROR = 'error', 'Error'


class VerificationLog(models.Model):
    """Log of all verification attempts"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Credential being verified
    credential = models.ForeignKey(
        'credentials.Credential',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verification_logs'
    )
    credential_id_searched = models.CharField(max_length=100, blank=True)
    
    # Who verified
    verifier = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verifications_performed'
    )
    verifier_company = models.CharField(max_length=200, blank=True)
    verifier_email = models.EmailField(blank=True)
    
    # Verification details
    method = models.CharField(
        max_length=20,
        choices=VerificationMethod.choices,
        default=VerificationMethod.CREDENTIAL_ID
    )
    result = models.CharField(
        max_length=20,
        choices=VerificationResult.choices
    )
    
    # Request metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    response_time_ms = models.PositiveIntegerField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Verification Log'
        verbose_name_plural = 'Verification Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.credential_id_searched} - {self.result} - {self.created_at}"


class VerificationReport(models.Model):
    """Aggregated verification reports"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Report period
    report_date = models.DateField(unique=True)
    
    # Counts
    total_verifications = models.PositiveIntegerField(default=0)
    valid_verifications = models.PositiveIntegerField(default=0)
    invalid_verifications = models.PositiveIntegerField(default=0)
    revoked_verifications = models.PositiveIntegerField(default=0)
    not_found_verifications = models.PositiveIntegerField(default=0)
    
    # By method
    by_credential_id = models.PositiveIntegerField(default=0)
    by_blockchain_hash = models.PositiveIntegerField(default=0)
    by_qr_code = models.PositiveIntegerField(default=0)
    by_share_link = models.PositiveIntegerField(default=0)
    by_api = models.PositiveIntegerField(default=0)
    
    # Performance
    avg_response_time_ms = models.FloatField(default=0)
    
    # Top verifiers
    top_verifiers = models.JSONField(default=list, blank=True)
    top_credentials = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Verification Report'
        verbose_name_plural = 'Verification Reports'
        ordering = ['-report_date']


class FraudAlert(models.Model):
    """Suspicious verification activity alerts"""
    
    class AlertType(models.TextChoices):
        MULTIPLE_FAILURES = 'multiple_failures', 'Multiple Failed Verifications'
        UNUSUAL_PATTERN = 'unusual_pattern', 'Unusual Verification Pattern'
        REVOKED_ACCESS = 'revoked_access', 'Attempting to Verify Revoked Credential'
        FAKE_CREDENTIAL = 'fake_credential', 'Potential Fake Credential'
        BRUTE_FORCE = 'brute_force', 'Brute Force Attempt'
    
    class AlertSeverity(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    alert_type = models.CharField(max_length=30, choices=AlertType.choices)
    severity = models.CharField(
        max_length=20,
        choices=AlertSeverity.choices,
        default=AlertSeverity.MEDIUM
    )
    
    # Related entities
    credential = models.ForeignKey(
        'credentials.Credential',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    institution = models.ForeignKey(
        'institutions.Institution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Details
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Fraud Alert'
        verbose_name_plural = 'Fraud Alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert_type} - {self.severity} - {self.created_at}"

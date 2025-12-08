"""
Credential models for blockchain-verified academic credentials
"""
import uuid
import hashlib
import json
from django.db import models
from django.utils import timezone


class CredentialStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PENDING = 'pending', 'Pending Approval'
    ISSUED = 'issued', 'Issued'
    REVOKED = 'revoked', 'Revoked'
    EXPIRED = 'expired', 'Expired'


class CredentialType(models.TextChoices):
    DEGREE = 'degree', 'Degree Certificate'
    DIPLOMA = 'diploma', 'Diploma'
    CERTIFICATE = 'certificate', 'Certificate'
    TRANSCRIPT = 'transcript', 'Transcript'
    AWARD = 'award', 'Award/Honor'
    PROFESSIONAL = 'professional', 'Professional Certification'


class Credential(models.Model):
    """Main credential model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Credential ID (human-readable)
    credential_id = models.CharField(max_length=50, unique=True, db_index=True)
    
    # Type and status
    credential_type = models.CharField(
        max_length=20,
        choices=CredentialType.choices,
        default=CredentialType.DEGREE
    )
    status = models.CharField(
        max_length=20,
        choices=CredentialStatus.choices,
        default=CredentialStatus.DRAFT
    )
    
    # Holder (Student)
    holder = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='credentials'
    )
    holder_name = models.CharField(max_length=200)  # Name as it appears on credential
    holder_student_id = models.CharField(max_length=50, blank=True)
    holder_date_of_birth = models.DateField(blank=True, null=True)
    
    # Institution
    institution = models.ForeignKey(
        'institutions.Institution',
        on_delete=models.PROTECT,
        related_name='credentials'
    )
    
    # Program/Course details
    program = models.ForeignKey(
        'institutions.Program',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='credentials'
    )
    program_name = models.CharField(max_length=300)
    degree_level = models.CharField(max_length=50, blank=True)
    major = models.CharField(max_length=200, blank=True)
    minor = models.CharField(max_length=200, blank=True)
    specialization = models.CharField(max_length=200, blank=True)
    
    # Academic details
    grade = models.CharField(max_length=50, blank=True)  # e.g., "First Class", "3.8 GPA"
    honors = models.CharField(max_length=200, blank=True)  # e.g., "Cum Laude"
    credits_earned = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    
    # Dates
    enrollment_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    
    # Blockchain data
    blockchain_hash = models.CharField(max_length=100, blank=True, db_index=True)
    blockchain_tx_id = models.CharField(max_length=100, blank=True)
    block_number = models.PositiveIntegerField(blank=True, null=True)
    ipfs_hash = models.CharField(max_length=100, blank=True)
    
    # Document
    document = models.FileField(upload_to='credentials/', blank=True, null=True)
    document_hash = models.CharField(max_length=100, blank=True)
    
    # QR Code
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    verification_url = models.URLField(blank=True)
    
    # Issuer info
    issued_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_credentials'
    )
    issuer_signature = models.TextField(blank=True)
    
    # Revocation
    revoked_at = models.DateTimeField(blank=True, null=True)
    revoked_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revoked_credentials'
    )
    revocation_reason = models.TextField(blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Credential'
        verbose_name_plural = 'Credentials'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.credential_id} - {self.holder_name}"
    
    def generate_credential_id(self):
        """Generate a unique credential ID"""
        year = timezone.now().year
        country_code = self.institution.country_code or 'XX'
        random_suffix = str(uuid.uuid4().hex[:6]).upper()
        return f"CERT-{year}-{country_code}-{random_suffix}"
    
    def calculate_hash(self):
        """Calculate blockchain hash for the credential"""
        data = {
            'credential_id': self.credential_id,
            'holder_name': self.holder_name,
            'institution': str(self.institution.id),
            'program_name': self.program_name,
            'completion_date': str(self.completion_date),
            'issue_date': str(self.issue_date),
        }
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def get_verification_url(self, request=None):
        """Generate verification URL for this credential using current request host"""
        from django.conf import settings
        
        # Always prefer request host (most accurate - uses actual current host)
        if request:
            scheme = request.scheme
            domain = request.get_host()
        else:
            # Try to get from BruteBuster middleware thread-local request
            try:
                from apps.brutebuster.middleware import get_request
                req = get_request()
                if req:
                    scheme = req.scheme
                    domain = req.get_host()
                else:
                    raise AttributeError()
            except:
                # Fallback: Use ALLOWED_HOSTS (first entry) or default
                if hasattr(settings, 'ALLOWED_HOSTS') and settings.ALLOWED_HOSTS:
                    domain = settings.ALLOWED_HOSTS[0]
                    # Keep port if present (e.g., 'localhost:8000')
                else:
                    domain = 'localhost:8000' if settings.DEBUG else 'localhost'
                
                scheme = 'https' if not settings.DEBUG else 'http'
        
        return f"{scheme}://{domain}/credentials/verify/{self.credential_id}/"
    
    def generate_qr_code(self, save=True, request=None):
        """Generate QR code for this credential using current request host"""
        # Always use current request's verification URL (not stored one)
        current_verification_url = self.get_verification_url(request=request)
        
        # Update stored verification_url to use current host
        self.verification_url = current_verification_url
        
        try:
            from .qr_generator import generate_qr_code_file
            # Generate QR code with current verification URL (not stored one)
            qr_file = generate_qr_code_file(
                current_verification_url,  # Use current URL, not self.verification_url
                filename=f'qr_{self.credential_id}.png',
                size=300
            )
            self.qr_code.save(f'qr_{self.credential_id}.png', qr_file, save=False)
            if save:
                self.save(update_fields=['qr_code', 'verification_url'])
            return True
        except ImportError:
            # qrcode library not installed
            return False
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return False
    
    def save(self, *args, **kwargs):
        if not self.credential_id:
            self.credential_id = self.generate_credential_id()
        
        # Generate verification URL if not set
        if not self.verification_url:
            self.verification_url = self.get_verification_url()
        
        super().save(*args, **kwargs)


class CredentialShare(models.Model):
    """Track credential sharing"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    credential = models.ForeignKey(
        Credential,
        on_delete=models.CASCADE,
        related_name='shares'
    )
    
    # Share details
    share_token = models.CharField(max_length=100, unique=True)
    shared_with_email = models.EmailField(blank=True)
    shared_with_company = models.CharField(max_length=200, blank=True)
    
    # Access control
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    max_views = models.PositiveIntegerField(blank=True, null=True)
    view_count = models.PositiveIntegerField(default=0)
    
    # Privacy settings
    hide_grade = models.BooleanField(default=False)
    hide_student_id = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Credential Share'
        verbose_name_plural = 'Credential Shares'
    
    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        if self.max_views and self.view_count >= self.max_views:
            return False
        return True


class CredentialBatch(models.Model):
    """Batch issuance of credentials"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        'institutions.Institution',
        on_delete=models.CASCADE,
        related_name='credential_batches'
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Batch status
    class BatchStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    
    status = models.CharField(
        max_length=20,
        choices=BatchStatus.choices,
        default=BatchStatus.DRAFT
    )
    
    total_count = models.PositiveIntegerField(default=0)
    processed_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    
    # File upload
    source_file = models.FileField(upload_to='batch_uploads/', blank=True, null=True)
    
    # Created by
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Credential Batch'
        verbose_name_plural = 'Credential Batches'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.institution.name}"


class BlockchainTransaction(models.Model):
    """Record of blockchain transactions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    credential = models.ForeignKey(
        Credential,
        on_delete=models.CASCADE,
        related_name='blockchain_transactions'
    )
    
    class TransactionType(models.TextChoices):
        ISSUE = 'issue', 'Credential Issued'
        REVOKE = 'revoke', 'Credential Revoked'
        UPDATE = 'update', 'Credential Updated'
    
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    transaction_hash = models.CharField(max_length=100, unique=True)
    block_number = models.PositiveIntegerField()
    gas_used = models.PositiveIntegerField(blank=True, null=True)
    
    # Status
    is_confirmed = models.BooleanField(default=False)
    confirmations = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Blockchain Transaction'
        verbose_name_plural = 'Blockchain Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_hash[:16]}..."

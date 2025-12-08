"""
Institution models for CertChain
"""
import uuid
from django.db import models
from django.utils import timezone


class InstitutionType(models.TextChoices):
    UNIVERSITY = 'university', 'University'
    COLLEGE = 'college', 'College'
    POLYTECHNIC = 'polytechnic', 'Polytechnic'
    VOCATIONAL = 'vocational', 'Vocational Institute'
    PROFESSIONAL = 'professional', 'Professional Body'
    GOVERNMENT = 'government', 'Government Agency'


class AccreditationStatus(models.TextChoices):
    ACCREDITED = 'accredited', 'Accredited'
    PENDING = 'pending', 'Pending Review'
    PROBATION = 'probation', 'On Probation'
    REVOKED = 'revoked', 'Accreditation Revoked'
    NOT_ACCREDITED = 'not_accredited', 'Not Accredited'


class Institution(models.Model):
    """Institution model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    name = models.CharField(max_length=300, db_index=True)
    short_name = models.CharField(max_length=50, blank=True)
    institution_type = models.CharField(
        max_length=20,
        choices=InstitutionType.choices,
        default=InstitutionType.UNIVERSITY
    )
    
    # WHED Integration
    whed_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    # Contact info
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    
    # Location
    country = models.CharField(max_length=100, db_index=True)
    country_code = models.CharField(max_length=3, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    
    # Branding
    logo = models.ImageField(upload_to='institution_logos/', blank=True, null=True)
    
    # Accreditation
    accreditation_status = models.CharField(
        max_length=20,
        choices=AccreditationStatus.choices,
        default=AccreditationStatus.PENDING
    )
    accreditation_body = models.CharField(max_length=200, blank=True)
    accreditation_date = models.DateField(blank=True, null=True)
    accreditation_expiry = models.DateField(blank=True, null=True)
    
    # Founding
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    
    # Platform status
    is_partner = models.BooleanField(default=False)
    partner_since = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Blockchain
    blockchain_address = models.CharField(max_length=100, blank=True)
    public_key = models.TextField(blank=True)
    
    # Statistics
    total_credentials_issued = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Institution'
        verbose_name_plural = 'Institutions'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Program(models.Model):
    """Academic programs offered by institutions"""
    
    class DegreeLevel(models.TextChoices):
        CERTIFICATE = 'certificate', 'Certificate'
        DIPLOMA = 'diploma', 'Diploma'
        ASSOCIATE = 'associate', 'Associate Degree'
        BACHELOR = 'bachelor', 'Bachelor\'s Degree'
        MASTER = 'master', 'Master\'s Degree'
        DOCTORATE = 'doctorate', 'Doctorate'
        PROFESSIONAL = 'professional', 'Professional Degree'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name='programs'
    )
    
    name = models.CharField(max_length=300)
    code = models.CharField(max_length=50, blank=True)
    degree_level = models.CharField(
        max_length=20,
        choices=DegreeLevel.choices,
        default=DegreeLevel.BACHELOR
    )
    department = models.CharField(max_length=200, blank=True)
    faculty = models.CharField(max_length=200, blank=True)
    duration_years = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Program'
        verbose_name_plural = 'Programs'
        ordering = ['name']
        unique_together = ['institution', 'code']
    
    def __str__(self):
        return f"{self.name} ({self.institution.short_name or self.institution.name})"


class AccreditationRecord(models.Model):
    """Historical accreditation records"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name='accreditation_history'
    )
    
    accreditation_body = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=AccreditationStatus.choices)
    granted_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    certificate_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    # Document
    certificate_document = models.FileField(
        upload_to='accreditation_certificates/',
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Accreditation Record'
        verbose_name_plural = 'Accreditation Records'
        ordering = ['-granted_date']
    
    def __str__(self):
        return f"{self.institution.name} - {self.accreditation_body} ({self.status})"

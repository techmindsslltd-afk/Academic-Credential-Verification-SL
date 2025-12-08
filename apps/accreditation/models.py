"""
Accreditation and WHED integration models
"""
import uuid
from django.db import models


class AccreditationBody(models.Model):
    """Accreditation bodies and organizations"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=300)
    short_name = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    
    # Type
    class BodyType(models.TextChoices):
        NATIONAL = 'national', 'National Agency'
        REGIONAL = 'regional', 'Regional Body'
        INTERNATIONAL = 'international', 'International Organization'
        PROFESSIONAL = 'professional', 'Professional Association'
    
    body_type = models.CharField(
        max_length=20,
        choices=BodyType.choices,
        default=BodyType.NATIONAL
    )
    
    # Contact
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    
    # Status
    is_recognized = models.BooleanField(default=True)
    recognized_by = models.CharField(max_length=200, blank=True)
    
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Accreditation Body'
        verbose_name_plural = 'Accreditation Bodies'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.country})"


class WHEDRecord(models.Model):
    """UNESCO WHED database records"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # WHED data
    whed_id = models.CharField(max_length=50, unique=True, db_index=True)
    institution_name = models.CharField(max_length=300, db_index=True)
    institution_name_local = models.CharField(max_length=300, blank=True)
    
    # Location
    country = models.CharField(max_length=100, db_index=True)
    country_code = models.CharField(max_length=3)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    
    # Contact
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    
    # Institution type
    institution_type = models.CharField(max_length=100, blank=True)
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    
    # Accreditation
    is_accredited = models.BooleanField(default=True)
    accreditation_body = models.CharField(max_length=200, blank=True)
    
    # Linked institution (if partner)
    linked_institution = models.OneToOneField(
        'institutions.Institution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whed_record'
    )
    
    # Metadata
    last_updated = models.DateField(blank=True, null=True)
    data_source = models.CharField(max_length=100, default='UNESCO WHED')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'WHED Record'
        verbose_name_plural = 'WHED Records'
        ordering = ['institution_name']
    
    def __str__(self):
        return f"{self.institution_name} ({self.whed_id})"


class AccreditationLookupLog(models.Model):
    """Log of accreditation lookups"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Search details
    search_query = models.CharField(max_length=300)
    search_type = models.CharField(max_length=50)  # institution_name, whed_id, country
    
    # Results
    results_count = models.PositiveIntegerField(default=0)
    whed_record = models.ForeignKey(
        WHEDRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # User
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Accreditation Lookup Log'
        verbose_name_plural = 'Accreditation Lookup Logs'
        ordering = ['-created_at']

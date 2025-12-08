# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present TechMinds SL Ltd
"""
from __future__ import absolute_import

from django.db import models
from apps.accounts.models import User
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.template.defaultfilters import truncatechars, striptags
from django.utils.safestring import mark_safe
from django.urls import reverse

# Create your models here.



class GeneralSettings(models.Model):
    site_name = models.CharField(max_length=255, blank=True, null=True)
    site_name_abb = models.CharField(max_length=255, blank=True, null=True)
    slogan = models.CharField(max_length=255, blank=True, null=True)
    primary_color = models.CharField(max_length=255, blank=True, null=True)
    secondary_color = models.CharField(max_length=255, blank=True, null=True)
    file = models.ImageField(upload_to='logo', blank=True, null=True)
    file_2 = models.ImageField(upload_to='logo_2s', blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    email2 = models.EmailField(max_length=255, blank=True, null=True)
    site_desc = models.TextField(max_length=255, blank=True, null=True)
    site_keyword = models.TextField(max_length=255, blank=True, null=True)
    google_code = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    street2 = models.CharField(max_length=255, blank=True, null=True)
    city2 = models.CharField(max_length=255, blank=True, null=True)
    country2 = models.CharField(max_length=255, blank=True, null=True)
    phone2 = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)
    twitter = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.CharField(max_length=255, blank=True, null=True)
    instagram = models.CharField(max_length=255, blank=True, null=True)
    google = models.CharField(max_length=255, blank=True, null=True)
    reddit = models.CharField(max_length=255, blank=True, null=True)
    tumblr = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    data_sync = models.BooleanField(default=False, null=True, blank=True)
    created_online = models.BooleanField(default=False, null=True, blank=True)
    def __str__(self):
        return self.site_name



# Contact Message Model
class ContactMessage(models.Model):
    """Model for storing contact form submissions"""
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="Full Name")
    email = models.EmailField(verbose_name="Email Address")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone Number")
    subject = models.CharField(max_length=255, verbose_name="Subject")
    interest = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        choices=[
            ('volunteer', 'Volunteering'),
            ('donate', 'Making a Donation'),
            ('partner', 'Partnership Opportunities'),
            ('programs', 'Program Information'),
            ('other', 'Other')
        ],
        verbose_name="Area of Interest"
    )
    message = models.TextField(verbose_name="Message")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Status")
    notes = models.TextField(blank=True, null=True, verbose_name="Internal Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Received At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    replied_at = models.DateTimeField(blank=True, null=True, verbose_name="Replied At")
    replied_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_replies', verbose_name="Replied By")
    
    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    def mark_as_read(self, user=None):
        """Mark message as read"""
        if self.status == 'new':
            self.status = 'read'
            self.save(update_fields=['status'])
    
    def mark_as_replied(self, user):
        """Mark message as replied"""
        self.status = 'replied'
        self.replied_by = user
        from django.utils import timezone
        self.replied_at = timezone.now()
        self.save(update_fields=['status', 'replied_by', 'replied_at'])
    
    def archive(self):
        """Archive the message"""
        self.status = 'archived'
        self.save(update_fields=['status'])


class Visitor(models.Model):
    """Model for tracking website visitors"""
    
    # Visitor Information
    ip_address = models.GenericIPAddressField(verbose_name="IP Address")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    referer = models.URLField(blank=True, null=True, verbose_name="Referer")
    
    # Page Information
    path = models.CharField(max_length=500, verbose_name="Page Path")
    full_path = models.URLField(blank=True, null=True, verbose_name="Full URL")
    
    # User Information (if logged in)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits',
        verbose_name="User"
    )
    
    # Session Information
    session_key = models.CharField(max_length=40, blank=True, null=True, verbose_name="Session Key")
    
    # Device Information
    device_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Device Type")
    browser = models.CharField(max_length=100, blank=True, null=True, verbose_name="Browser")
    os = models.CharField(max_length=100, blank=True, null=True, verbose_name="Operating System")
    
    # Location Information (optional - can be populated via IP geolocation)
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Country")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="City")
    
    # Timestamp
    visited_at = models.DateTimeField(auto_now_add=True, verbose_name="Visited At")
    
    class Meta:
        verbose_name = "Visitor"
        verbose_name_plural = "Visitors"
        ordering = ['-visited_at']
        indexes = [
            models.Index(fields=['-visited_at']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['path']),
        ]
    
    def __str__(self):
        return f"{self.ip_address} - {self.path} - {self.visited_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_unique_visitor(self):
        """Check if this is a unique visitor (first visit from this IP in last 24 hours)"""
        from django.utils import timezone
        from datetime import timedelta
        yesterday = timezone.now() - timedelta(days=1)
        return not Visitor.objects.filter(
            ip_address=self.ip_address,
            visited_at__gte=yesterday
        ).exclude(id=self.id).exists()
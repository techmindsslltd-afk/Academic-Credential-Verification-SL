# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present TechMinds SL Ltd
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import *


# ============= Program Related Admin =============

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'path', 'browser', 'device_type', 'user', 'visited_at')
    list_filter = ('browser', 'os', 'device_type', 'visited_at', 'country')
    search_fields = ('ip_address', 'path', 'user__username', 'user_agent')
    readonly_fields = ('visited_at',)
    date_hierarchy = 'visited_at'
    ordering = ('-visited_at',)
    
    fieldsets = (
        ('Visitor Information', {
            'fields': ('ip_address', 'user', 'session_key')
        }),
        ('Page Information', {
            'fields': ('path', 'full_path', 'referer')
        }),
        ('Device Information', {
            'fields': ('browser', 'os', 'device_type', 'user_agent')
        }),
        ('Location Information', {
            'fields': ('country', 'city'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('visited_at',)
        }),
    )

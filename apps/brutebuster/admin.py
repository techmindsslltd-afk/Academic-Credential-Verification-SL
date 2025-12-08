# BruteBuster by Cyber Security Consulting (www.csc.bg)

"""Admin settings for the BruteBuster module"""

from django.contrib import admin
from .models import FailedAttempt


class AdminFailedAttempt(admin.ModelAdmin):
    list_display = ('email', 'IP', 'failures', 'timestamp', 'blocked')
    search_fields = ('email', 'IP',)


admin.site.register(FailedAttempt, AdminFailedAttempt)

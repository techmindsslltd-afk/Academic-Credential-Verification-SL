from django import template
from django.contrib.auth.models import Group
from apps.accounts.models import User


from django import template

register = template.Library()

@register.filter
def is_extension(file_url, extensions):
    """
    Check if a file URL ends with one of the specified extensions.
    Example usage: {{ file_url|is_extension:"pdf,doc,docx" }}
    """
    valid_extensions = extensions.split(',')
    return any(file_url.lower().endswith(f".{ext.strip()}") for ext in valid_extensions)

from django import template
from apps.accounts.models import User, UserRole

register = template.Library()

@register.simple_tag
def get_institution_student_count(user):
    """Get the count of students for an institution admin's institution"""
    if not user or not user.is_authenticated:
        return 0
    
    if user.role != UserRole.INSTITUTION_ADMIN:
        return 0
    
    try:
        institution = user.institution_admin_profile.institution
        if not institution:
            return 0
        
        count = User.objects.filter(
            role=UserRole.STUDENT,
            student_profile__institution=institution
        ).count()
        
        # Format with comma separator for large numbers
        if count >= 1000:
            return f"{count:,}"
        return str(count)
    except:
        return 0


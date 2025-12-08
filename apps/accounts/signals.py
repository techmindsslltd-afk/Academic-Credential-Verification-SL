"""
Signals for automatic profile creation
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserRole, StudentProfile, EmployerProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create appropriate profile based on user role"""
    if created:
        if instance.role == UserRole.STUDENT:
            StudentProfile.objects.get_or_create(user=instance)
        elif instance.role == UserRole.EMPLOYER:
            EmployerProfile.objects.get_or_create(
                user=instance,
                defaults={'company_name': f"{instance.full_name}'s Company"}
            )

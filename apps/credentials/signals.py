"""
Signals for credential events
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Credential, CredentialStatus


@receiver(pre_save, sender=Credential)
def set_credential_hash(sender, instance, **kwargs):
    """Calculate and set blockchain hash before saving"""
    if instance.status == CredentialStatus.ISSUED and not instance.blockchain_hash:
        instance.blockchain_hash = instance.calculate_hash()


@receiver(post_save, sender=Credential)
def update_institution_stats(sender, instance, created, **kwargs):
    """Update institution statistics when credential is issued"""
    if created or instance.status == CredentialStatus.ISSUED:
        from django.db.models import Count
        institution = instance.institution
        institution.total_credentials_issued = Credential.objects.filter(
            institution=institution,
            status=CredentialStatus.ISSUED
        ).count()
        institution.save(update_fields=['total_credentials_issued'])

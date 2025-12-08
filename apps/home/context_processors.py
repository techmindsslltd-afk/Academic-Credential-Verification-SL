from apps.home.models import GeneralSettings
from apps.accounts.models import *

def general_settings(request):
    # Retrieve GeneralSettings object
    settings_obj = GeneralSettings.objects.all().first()  # Assuming id=1 is the correct id

    # Return it in a dictionary to be added to the template context
    return {'settings': settings_obj}

def mysignature(request):
    # Retrieve GeneralSettings object
    try:
        mysignature =  Signature.objects.get(recordOwner=request.user.id)  # Assuming id=1 is the correct id
    except:  
        mysignature = None
    # Return it in a dictionary to be added to the template context
    return {'mysignature': mysignature}

def sidebar_stats(request):
    """Provide sidebar statistics for all templates"""
    stats = {
        'institution_student_count': 0,
    }
    
    if request.user.is_authenticated and request.user.role == 'institution_admin':
        try:
            institution = request.user.institution_admin_profile.institution
            if institution:
                from apps.accounts.models import User, UserRole
                count = User.objects.filter(
                    role=UserRole.STUDENT,
                    student_profile__institution=institution
                ).count()
                stats['institution_student_count'] = count
        except:
            pass
    
    return stats

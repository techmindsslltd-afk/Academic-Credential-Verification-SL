# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present TechMinds SL Ltd
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse 

# -*- encoding: utf-8 -*-
"""  
Copyright (c) 2024 - present TechMinds SL Ltd
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from django.db.models import Sum
from apps.accounts.models import User
import sweetify
import json
from django.http import JsonResponse
import datetime
from django.views import View
### accout creations
from django.contrib.auth.models import Group
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string, get_template
from apps.accounts.utils import account_activation_token 
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
   
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from apps.staff.models import *
from apps.home.models import *
from .models import *
from .forms import *

from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMessage
from django.conf import settings as setting
from django.db.models.deletion import ProtectedError
from apps.decorators import *


    
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.db.models import Sum


from django.template import loader, TemplateDoesNotExist
from django.core.exceptions import PermissionDenied 
import os

from django.utils.translation import activate

from django.http import JsonResponse
from django.utils.translation import get_language

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import get_language
from django.core.cache import cache
from django.db.models import Count 

from rapidfuzz import process, fuzz 
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy 
from django.utils.timesince import timesince


def get_time_ago(datetime_obj):
    """Helper function to format time ago in a human-readable format"""
    if not datetime_obj:
        return "Just now"
    time_ago = timesince(datetime_obj)
    # Format the output to be more concise
    if "minute" in time_ago.lower():
        time_ago = time_ago.split(",")[0] + " ago"
    elif "hour" in time_ago.lower():
        time_ago = time_ago.split(",")[0] + " ago"
    elif "day" in time_ago.lower():
        time_ago = time_ago.split(",")[0] + " ago"
    elif "week" in time_ago.lower():
        time_ago = time_ago.split(",")[0] + " ago"
    elif "month" in time_ago.lower():
        time_ago = time_ago.split(",")[0] + " ago"
    elif "year" in time_ago.lower():
        time_ago = time_ago.split(",")[0] + " ago"
    else:
        time_ago = time_ago + " ago" if "ago" not in time_ago.lower() else time_ago
    return time_ago


def set_language(request):
    language = request.GET.get('language', 'en')  # Default to 'en' if no language is passed
    activate(language)  # Activate the selected language
    response = JsonResponse({'message': 'Language changed successfully.'})
    response.set_cookie('django_language', language)  # Set the language in a cookie
    return response


def index(request):
    transl_OLD = request.GET.get('transl_OLD')  # Default to English
    users = User.objects.all()
    
    # Import models for statistics
    from apps.credentials.models import Credential, CredentialStatus
    from apps.verifications.models import VerificationLog
    from apps.institutions.models import Institution
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    # Calculate statistics from database
    # 1. Credentials verified annually (total verifications in the last year)
    one_year_ago = timezone.now() - timedelta(days=365)
    credentials_verified_annually = VerificationLog.objects.filter(
        created_at__gte=one_year_ago
    ).count()
    
    # 2. Universities in database (total active institutions)
    universities_in_database = Institution.objects.filter(is_active=True).count()
    
    # 3. Countries covered (unique countries from institutions)
    countries_covered = Institution.objects.filter(
        is_active=True,
        country__isnull=False
    ).values('country').distinct().count()
    
    # 4. Fraudulent credentials passed (should be 0, but we can show revoked credentials)
    fraudulent_credentials = Credential.objects.filter(
        status=CredentialStatus.REVOKED
    ).count()
    
    # Additional stats for context
    total_credentials = Credential.objects.count()
    total_verifications = VerificationLog.objects.count()
    total_institutions = Institution.objects.count()
    
    # Accreditation page statistics
    # UNESCO WHED stats (approximate - you can adjust based on your WHED integration)
    whed_institutions = 21000  # This would come from WHED API if integrated
    whed_countries = countries_covered  # Use actual countries from database
    whed_accreditation_bodies = 4500  # This would come from WHED API if integrated
    
    # Partner institutions (institutions that are partners)
    partner_institutions = Institution.objects.filter(is_partner=True, is_active=True).count()
    
    # Accreditation records count
    from apps.institutions.models import AccreditationRecord, AccreditationStatus
    accreditation_records = AccreditationRecord.objects.filter(
        status=AccreditationStatus.ACCREDITED
    ).count()
    
    # Get unique countries and institution types for search dropdowns
    from apps.institutions.models import InstitutionType
    unique_countries = Institution.objects.filter(
        is_active=True,
        country__isnull=False
    ).values_list('country', flat=True).distinct().order_by('country')
    institution_types = InstitutionType.choices

    # Wallet data for logged-in users
    wallet_credentials = []
    wallet_stats = {
        'credentials_count': 0,
        'verifications_count': 0,
        'shares_count': 0
    }
    wallet_activities = []
    
    if request.user.is_authenticated:
        from apps.accounts.models import UserRole
        from apps.verifications.models import VerificationLog, VerificationResult
        from apps.credentials.models import CredentialShare
        from django.utils import timezone
        from datetime import timedelta
        
        # Get user's credentials
        if request.user.role == UserRole.STUDENT:
            wallet_credentials = Credential.objects.filter(
                holder=request.user
            ).select_related('institution', 'program').order_by('-issue_date', '-created_at')
            
            wallet_stats['credentials_count'] = wallet_credentials.count()
            
            # Get verification count for user's credentials
            credential_ids = wallet_credentials.values_list('id', flat=True)
            wallet_stats['verifications_count'] = VerificationLog.objects.filter(
                credential_id__in=credential_ids
            ).count()
            
            # Get share count for user's credentials
            wallet_stats['shares_count'] = CredentialShare.objects.filter(
                credential__holder=request.user
            ).count()
            
            # Get recent activities (last 10)
            recent_verifications = VerificationLog.objects.filter(
                credential__holder=request.user
            ).select_related('credential', 'credential__institution', 'verifier').order_by('-created_at')[:10]
            
            recent_shares = CredentialShare.objects.filter(
                credential__holder=request.user
            ).select_related('credential', 'credential__institution').order_by('-created_at')[:10]
            
            # Combine and format activities
            for log in recent_verifications:
                activity_text = ""
                if log.result == VerificationResult.VALID:
                    if log.verifier_company:
                        activity_text = f"{log.verifier_company} verified your {log.credential.degree_level or 'credential'}"
                    elif log.verifier:
                        activity_text = f"{log.verifier.full_name or log.verifier.email} verified your {log.credential.degree_level or 'credential'}"
                    else:
                        activity_text = f"Your {log.credential.degree_level or 'credential'} was verified"
                wallet_activities.append({
                    'type': 'success',
                    'text': activity_text,
                    'time': log.created_at,
                    'time_ago': get_time_ago(log.created_at)
                })
            
            for share in recent_shares:
                recipient = share.shared_with_email or share.shared_with_company or 'recipient'
                wallet_activities.append({
                    'type': 'info',
                    'text': f"You shared credentials with {recipient}",
                    'time': share.created_at,
                    'time_ago': get_time_ago(share.created_at)
                })
            
            # Sort by time and limit to 10
            wallet_activities.sort(key=lambda x: x['time'], reverse=True)
            wallet_activities = wallet_activities[:10]

    context = {
        'segment': 'index',
        'users': users,
        'transl_OLD': transl_OLD,
        # Statistics from database
        'credentials_verified_annually': credentials_verified_annually,
        'universities_in_database': universities_in_database,
        'countries_covered': countries_covered,
        'fraudulent_credentials': fraudulent_credentials,
        'total_credentials': total_credentials,
        'total_verifications': total_verifications,
        'total_institutions': total_institutions,
        # Accreditation page statistics
        'whed_institutions': whed_institutions,
        'whed_countries': whed_countries,
        'whed_accreditation_bodies': whed_accreditation_bodies,
        'partner_institutions': partner_institutions,
        'accreditation_records': accreditation_records,
        # For search dropdowns
        'unique_countries': unique_countries,
        'institution_types': institution_types,
        # Wallet data
        'wallet_credentials': wallet_credentials,
        'wallet_stats': wallet_stats,
    } 
    
    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))




@login_required(login_url="/login/")
def dashboard(request):
    """Main Dashboard - Role-based dashboard"""
    from apps.credentials.models import Credential, CredentialStatus
    from apps.verifications.models import VerificationLog
    from apps.institutions.models import Institution, Program
    from apps.accounts.models import UserRole, InstitutionAdminProfile, StudentProfile
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    user = request.user
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Base statistics for all users
    context = {
        'segment': 'dashboard',
        'user': user,
    }
    
    # Role-specific statistics
    if user.role == 'super_admin':
        # Super Admin Statistics
        total_credentials = Credential.objects.count()
        issued_credentials = Credential.objects.filter(status=CredentialStatus.ISSUED).count()
        total_verifications = VerificationLog.objects.count()
        total_institutions = Institution.objects.count()
        active_institutions = Institution.objects.filter(is_active=True).count()
        total_users = User.objects.count()
        students = User.objects.filter(role=UserRole.STUDENT).count()
        institution_admins = User.objects.filter(role=UserRole.INSTITUTION_ADMIN).count()
        employers = User.objects.filter(role=UserRole.EMPLOYER).count()
        
        # Recent activity
        credentials_today = Credential.objects.filter(created_at__date=today).count()
        verifications_today = VerificationLog.objects.filter(created_at__date=today).count()
        users_today = User.objects.filter(date_joined__date=today).count()
        
        context.update({
            'total_credentials': total_credentials,
            'issued_credentials': issued_credentials,
            'total_verifications': total_verifications,
            'total_institutions': total_institutions,
            'active_institutions': active_institutions,
            'total_users': total_users,
            'students': students,
            'institution_admins': institution_admins,
            'employers': employers,
            'credentials_today': credentials_today,
            'verifications_today': verifications_today,
            'users_today': users_today,
        })
        
    elif user.role == 'student':
        # Student Statistics - Fetch user's credentials
        student_credentials = Credential.objects.filter(
            holder=user
        ).select_related('institution', 'program').order_by('-issue_date', '-created_at')
        
        total_credentials = student_credentials.count()
        issued_credentials = student_credentials.filter(status=CredentialStatus.ISSUED).count()
        
        context.update({
            'credentials': student_credentials,
            'credentials_count': total_credentials,
            'issued_credentials': issued_credentials,
            'total_credentials': total_credentials,
        })
        
    elif user.role == 'institution_admin':
        # Institution Admin Statistics
        try:
            admin_profile = user.institution_admin_profile
            institution = admin_profile.institution
            
            # Credentials for this institution
            institution_credentials = Credential.objects.filter(institution=institution)
            total_credentials = institution_credentials.count()
            issued_credentials = institution_credentials.filter(status=CredentialStatus.ISSUED).count()
            
            # Students for this institution
            institution_students = User.objects.filter(
                role=UserRole.STUDENT,
                student_profile__institution=institution
            )
            total_students = institution_students.count()
            
            # Programs for this institution
            institution_programs = Program.objects.filter(institution=institution)
            total_programs = institution_programs.count()
            active_programs = institution_programs.filter(is_active=True).count()
            
            # Verifications for this institution's credentials
            institution_verifications = VerificationLog.objects.filter(
                credential__institution=institution
            )
            total_verifications = institution_verifications.count()
            valid_verifications = institution_verifications.filter(result='valid').count()
            
            # Recent activity
            credentials_today = institution_credentials.filter(created_at__date=today).count()
            students_today = institution_students.filter(date_joined__date=today).count()
            
            context.update({
                'institution': institution,
                'total_credentials': total_credentials,
                'issued_credentials': issued_credentials,
                'total_students': total_students,
                'total_programs': total_programs,
                'active_programs': active_programs,
                'total_verifications': total_verifications,
                'valid_verifications': valid_verifications,
                'credentials_today': credentials_today,
                'students_today': students_today,
            })
        except InstitutionAdminProfile.DoesNotExist:
            pass
            
    elif user.role == 'student':
        # Student Statistics
        try:
            student_profile = user.student_profile
            student_credentials = Credential.objects.filter(
                holder=user
            ).select_related('institution', 'program').order_by('-issue_date', '-created_at')
            total_credentials = student_credentials.count()
            issued_credentials = student_credentials.filter(status=CredentialStatus.ISSUED).count()
            
            # Verifications of student's credentials
            student_verifications = VerificationLog.objects.filter(credential__holder=user)
            total_verifications = student_verifications.count()
            
            context.update({
                'student_profile': student_profile,
                'credentials': student_credentials,
                'credentials_count': total_credentials,
                'total_credentials': total_credentials,
                'issued_credentials': issued_credentials,
                'total_verifications': total_verifications,
            })
        except StudentProfile.DoesNotExist:
            # Still pass credentials even if profile doesn't exist
            student_credentials = Credential.objects.filter(
                holder=user
            ).select_related('institution', 'program').order_by('-issue_date', '-created_at')
            context.update({
                'credentials': student_credentials,
                'credentials_count': student_credentials.count(),
            })
            
    elif user.role == 'employer':
        # Employer Statistics
        employer_verifications = VerificationLog.objects.filter(verifier=user)
        total_verifications = employer_verifications.count()
        valid_verifications = employer_verifications.filter(result='valid').count()
        invalid_verifications = employer_verifications.filter(result='invalid').count()
        
        # Recent activity
        verifications_today = employer_verifications.filter(created_at__date=today).count()
        verifications_this_week = employer_verifications.filter(created_at__gte=week_ago).count()
        verifications_this_month = employer_verifications.filter(created_at__gte=month_ago).count()
        
        context.update({
            'total_verifications': total_verifications,
            'valid_verifications': valid_verifications,
            'invalid_verifications': invalid_verifications,
            'verifications_today': verifications_today,
            'verifications_this_week': verifications_this_week,
            'verifications_this_month': verifications_this_month,
        })

    html_template = loader.get_template('dashboard.html')
    return HttpResponse(html_template.render(context, request))


# ============================================================================
# SUPER ADMIN VIEWS
# ============================================================================

@login_required(login_url="/login/")
def super_admin_dashboard(request):
    """Super Admin Dashboard"""
    if request.user.role != 'super_admin':
        return redirect('dashboard')
    
    users = User.objects.filter(is_active=True)
    total_users = users.count()
    awaiting_users = User.objects.filter(is_active=False).count()
    
    context = {
        'segment': 'dashboard',
        'users': users,
        'total_users': total_users,
        'awaiting_users': awaiting_users,
        'user': request.user,
    }
    html_template = loader.get_template('dashboard.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def super_admin_institutions(request):
    """Super Admin - Institutions Management"""
    if request.user.role != 'super_admin':
        return redirect('dashboard')
    
    # Import Institution model and Paginator
    from apps.institutions.models import Institution, InstitutionType, AccreditationStatus
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    # Get search query and filters
    search_query = request.GET.get('search', '').strip()
    filter_type = request.GET.get('type', '')
    filter_country = request.GET.get('country', '')
    filter_status = request.GET.get('status', '')
    filter_partner = request.GET.get('partner', '')
    
    # Fetch institutions with search filter
    institutions = Institution.objects.all().order_by('name')
    
    # Apply search filter if query exists
    if search_query:
        from django.db.models import Q
        institutions = institutions.filter(
            Q(name__icontains=search_query) |
            Q(short_name__icontains=search_query) |
            Q(country__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(whed_id__icontains=search_query)
        )
    
    # Apply filters
    if filter_type:
        institutions = institutions.filter(institution_type=filter_type)
    if filter_country:
        institutions = institutions.filter(country__icontains=filter_country)
    if filter_status:
        institutions = institutions.filter(accreditation_status=filter_status)
    if filter_partner:
        institutions = institutions.filter(is_partner=(filter_partner == 'true'))
    
    # Pagination - 20 items per page
    paginator = Paginator(institutions, 20)
    page = request.GET.get('page', 1)
    
    try:
        institutions_page = paginator.page(page)
    except PageNotAnInteger:
        institutions_page = paginator.page(1)
    except EmptyPage:
        institutions_page = paginator.page(paginator.num_pages)
    
    # Get unique countries for filter dropdown
    countries = Institution.objects.values_list('country', flat=True).distinct().order_by('country')
    
    context = {
        'segment': 'institutions',
        'user': request.user,
        'institutions': institutions_page,
        'search_query': search_query,
        'paginator': paginator,
        'institution_types': InstitutionType.choices,
        'accreditation_statuses': AccreditationStatus.choices,
        'countries': countries,
        'filter_type': filter_type,
        'filter_country': filter_country,
        'filter_status': filter_status,
        'filter_partner': filter_partner,
    }
    html_template = loader.get_template('super-admin/institutions/index.html')
    return HttpResponse(html_template.render(context, request))


def _parse_bool(value):
    """Helper function to parse boolean values from various formats"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ['true', 'on', '1', 'yes']
    return bool(value)


@login_required(login_url="/login/")
@csrf_exempt
def institution_create(request):
    """Create a new institution"""
    if request.user.role != 'super_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        from apps.institutions.models import Institution
        import json
        
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
            
            institution = Institution.objects.create(
                name=data.get('name', ''),
                short_name=data.get('short_name', ''),
                institution_type=data.get('institution_type', 'university'),
                whed_id=data.get('whed_id', '') or None,
                website=data.get('website', '') or None,
                email=data.get('email', '') or None,
                phone=data.get('phone', ''),
                country=data.get('country', ''),
                country_code=data.get('country_code', ''),
                city=data.get('city', ''),
                address=data.get('address', ''),
                accreditation_status=data.get('accreditation_status', 'pending'),
                accreditation_body=data.get('accreditation_body', ''),
                founded_year=int(data.get('founded_year', 0)) if data.get('founded_year') else None,
                is_partner=_parse_bool(data.get('is_partner', False)),
                is_active=_parse_bool(data.get('is_active', True)),
                is_verified=_parse_bool(data.get('is_verified', False)),
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Institution created successfully',
                'institution': {
                    'id': str(institution.id),
                    'name': institution.name,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def institution_update(request, institution_id):
    """Update an institution"""
    if request.user.role != 'super_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    from apps.institutions.models import Institution
    import uuid
    
    try:
        institution = Institution.objects.get(id=uuid.UUID(str(institution_id)))
    except Institution.DoesNotExist:
        return JsonResponse({'error': 'Institution not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid institution ID'}, status=400)
    
    if request.method in ['POST', 'PUT', 'PATCH']:
        import json
        
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
            
            institution.name = data.get('name', institution.name)
            institution.short_name = data.get('short_name', institution.short_name)
            institution.institution_type = data.get('institution_type', institution.institution_type)
            institution.whed_id = data.get('whed_id', institution.whed_id) or None
            institution.website = data.get('website', institution.website) or None
            institution.email = data.get('email', institution.email) or None
            institution.phone = data.get('phone', institution.phone)
            institution.country = data.get('country', institution.country)
            institution.country_code = data.get('country_code', institution.country_code)
            institution.city = data.get('city', institution.city)
            institution.address = data.get('address', institution.address)
            institution.accreditation_status = data.get('accreditation_status', institution.accreditation_status)
            institution.accreditation_body = data.get('accreditation_body', institution.accreditation_body)
            if data.get('founded_year'):
                institution.founded_year = int(data.get('founded_year'))
            # Handle boolean values
            institution.is_partner = _parse_bool(data.get('is_partner', institution.is_partner))
            institution.is_active = _parse_bool(data.get('is_active', institution.is_active))
            institution.is_verified = _parse_bool(data.get('is_verified', institution.is_verified))
            
            institution.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Institution updated successfully',
                'institution': {
                    'id': str(institution.id),
                    'name': institution.name,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def institution_delete(request, institution_id):
    """Delete an institution"""
    if request.user.role != 'super_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    from apps.institutions.models import Institution
    import uuid
    
    try:
        institution = Institution.objects.get(id=uuid.UUID(str(institution_id)))
    except Institution.DoesNotExist:
        return JsonResponse({'error': 'Institution not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid institution ID'}, status=400)
    
    if request.method == 'POST' or request.method == 'DELETE':
        try:
            institution_name = institution.name
            institution.delete()
            return JsonResponse({
                'success': True,
                'message': f'Institution "{institution_name}" deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
def institution_detail(request, institution_id):
    """Get institution details"""
    if request.user.role != 'super_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    from apps.institutions.models import Institution
    import uuid
    
    try:
        institution = Institution.objects.get(id=uuid.UUID(str(institution_id)))
    except Institution.DoesNotExist:
        return JsonResponse({'error': 'Institution not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid institution ID'}, status=400)
    
    if request.method == 'GET':
        return JsonResponse({
            'id': str(institution.id),
            'name': institution.name,
            'short_name': institution.short_name,
            'institution_type': institution.institution_type,
            'whed_id': institution.whed_id,
            'website': institution.website,
            'email': institution.email,
            'phone': institution.phone,
            'country': institution.country,
            'country_code': institution.country_code,
            'city': institution.city,
            'address': institution.address,
            'accreditation_status': institution.accreditation_status,
            'accreditation_body': institution.accreditation_body,
            'accreditation_date': institution.accreditation_date.isoformat() if institution.accreditation_date else None,
            'accreditation_expiry': institution.accreditation_expiry.isoformat() if institution.accreditation_expiry else None,
            'founded_year': institution.founded_year,
            'is_partner': institution.is_partner,
            'partner_since': institution.partner_since.isoformat() if institution.partner_since else None,
            'is_active': institution.is_active,
            'is_verified': institution.is_verified,
            'blockchain_address': institution.blockchain_address,
            'total_credentials_issued': institution.total_credentials_issued,
            'total_students': institution.total_students,
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
def super_admin_users(request):
    """Super Admin - Users Management"""
    if request.user.role != 'super_admin':
        return redirect('dashboard')
    
    from apps.accounts.models import UserRole
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    # Get search query and filters
    search_query = request.GET.get('search', '').strip()
    filter_role = request.GET.get('role', '')
    filter_status = request.GET.get('status', '')
    filter_verified = request.GET.get('verified', '')
    
    # Fetch users
    users = User.objects.all().order_by('-date_joined')
    
    # Apply search filter if query exists
    if search_query:
        from django.db.models import Q
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Apply filters
    if filter_role:
        users = users.filter(role=filter_role)
    if filter_status:
        if filter_status == 'active':
            users = users.filter(is_active=True)
        elif filter_status == 'inactive':
            users = users.filter(is_active=False)
    if filter_verified:
        if filter_verified == 'verified':
            users = users.filter(is_verified=True)
        elif filter_verified == 'unverified':
            users = users.filter(is_verified=False)
    
    # Pagination - 20 items per page
    paginator = Paginator(users, 20)
    page = request.GET.get('page', 1)
    
    try:
        users_page = paginator.page(page)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)
    
    context = {
        'segment': 'users',
        'user': request.user,
        'users': users_page,
        'search_query': search_query,
        'paginator': paginator,
        'user_roles': UserRole.choices,
        'filter_role': filter_role,
        'filter_status': filter_status,
        'filter_verified': filter_verified,
    }
    html_template = loader.get_template('super-admin/users/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@csrf_exempt
def user_create(request):
    """Create a new user"""
    if request.user.role != 'super_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        from apps.accounts.models import UserRole
        import json
        
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
            
            # Validate required fields
            if not data.get('email'):
                return JsonResponse({'error': 'Email is required'}, status=400)
            if not data.get('first_name'):
                return JsonResponse({'error': 'First name is required'}, status=400)
            if not data.get('last_name'):
                return JsonResponse({'error': 'Last name is required'}, status=400)
            
            # Check if user already exists
            if User.objects.filter(email=data.get('email')).exists():
                return JsonResponse({'error': 'User with this email already exists'}, status=400)
            
            # Create user
            user = User.objects.create_user(
                email=data.get('email'),
                password=data.get('password', 'TempPassword123!'),  # Default password, should be changed
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                phone=data.get('phone', ''),
                role=data.get('role', UserRole.STUDENT),
                is_active=_parse_bool(data.get('is_active', True)),
                is_staff=_parse_bool(data.get('is_staff', False)),
                is_verified=_parse_bool(data.get('is_verified', False)),
                email_verified=_parse_bool(data.get('email_verified', False)),
            )
            
            return JsonResponse({
                'success': True,
                'message': 'User created successfully',
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'full_name': user.full_name,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def user_update(request, user_id):
    """Update a user"""
    if request.user.role != 'super_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    import uuid
    
    try:
        user = User.objects.get(id=uuid.UUID(str(user_id)))
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid user ID'}, status=400)
    
    # Prevent editing superuser status of other super admins
    if user.role == 'super_admin' and user.id != request.user.id:
        return JsonResponse({'error': 'Cannot modify other super admins'}, status=403)
    
    if request.method in ['POST', 'PUT', 'PATCH']:
        import json
        
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
            
            # Update user fields
            if data.get('email') and data.get('email') != user.email:
                if User.objects.filter(email=data.get('email')).exclude(id=user.id).exists():
                    return JsonResponse({'error': 'Email already in use'}, status=400)
                user.email = data.get('email')
            
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.phone = data.get('phone', user.phone)
            
            if data.get('role'):
                user.role = data.get('role')
            
            user.is_active = _parse_bool(data.get('is_active', user.is_active))
            user.is_staff = _parse_bool(data.get('is_staff', user.is_staff))
            user.is_verified = _parse_bool(data.get('is_verified', user.is_verified))
            user.email_verified = _parse_bool(data.get('email_verified', user.email_verified))
            
            # Update password if provided
            if data.get('password'):
                user.set_password(data.get('password'))
            
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'User updated successfully',
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'full_name': user.full_name,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def user_delete(request, user_id):
    """Delete a user"""
    if request.user.role != 'super_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    import uuid
    
    try:
        user = User.objects.get(id=uuid.UUID(str(user_id)))
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid user ID'}, status=400)
    
    # Prevent deleting yourself
    if user.id == request.user.id:
        return JsonResponse({'error': 'Cannot delete your own account'}, status=403)
    
    # Prevent deleting other super admins
    if user.role == 'super_admin':
        return JsonResponse({'error': 'Cannot delete super admin accounts'}, status=403)
    
    if request.method == 'POST' or request.method == 'DELETE':
        try:
            user_email = user.email
            user.delete()
            return JsonResponse({
                'success': True,
                'message': f'User "{user_email}" deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
def user_detail(request, user_id):
    """Get user details"""
    if request.user.role != 'super_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    import uuid
    
    try:
        user = User.objects.get(id=uuid.UUID(str(user_id)))
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid user ID'}, status=400)
    
    if request.method == 'GET':
        return JsonResponse({
            'id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'phone': user.phone,
            'role': user.role,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_verified': user.is_verified,
            'email_verified': user.email_verified,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'avatar': user.avatar.url if user.avatar else None,
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
def super_admin_accreditation(request):
    """Super Admin - Global Accreditation"""
    if request.user.role != 'super_admin':
        return redirect('dashboard')
    
    from apps.institutions.models import AccreditationRecord, Institution, AccreditationStatus
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.db.models import Q
    
    # Get search query and filters
    search_query = request.GET.get('search', '').strip()
    filter_institution = request.GET.get('institution', '')
    filter_status = request.GET.get('status', '')
    filter_accreditation_body = request.GET.get('accreditation_body', '')
    
    # Fetch all accreditation records
    accreditation_records = AccreditationRecord.objects.select_related('institution').order_by('-granted_date')
    
    # Apply search filter if query exists
    if search_query:
        accreditation_records = accreditation_records.filter(
            Q(institution__name__icontains=search_query) |
            Q(accreditation_body__icontains=search_query) |
            Q(certificate_number__icontains=search_query) |
            Q(institution__country__icontains=search_query)
        )
    
    # Apply filters
    if filter_institution:
        accreditation_records = accreditation_records.filter(institution_id=filter_institution)
    if filter_status:
        accreditation_records = accreditation_records.filter(status=filter_status)
    if filter_accreditation_body:
        accreditation_records = accreditation_records.filter(accreditation_body__icontains=filter_accreditation_body)
    
    # Pagination - 20 items per page
    paginator = Paginator(accreditation_records, 20)
    page = request.GET.get('page', 1)
    
    try:
        records_page = paginator.page(page)
    except PageNotAnInteger:
        records_page = paginator.page(1)
    except EmptyPage:
        records_page = paginator.page(paginator.num_pages)
    
    # Get all institutions for filter dropdown
    institutions = Institution.objects.all().order_by('name')
    
    # Get unique accreditation bodies for filter
    accreditation_bodies = AccreditationRecord.objects.exclude(accreditation_body='').values_list('accreditation_body', flat=True).distinct().order_by('accreditation_body')
    
    context = {
        'segment': 'accreditation',
        'user': request.user,
        'accreditation_records': records_page,
        'search_query': search_query,
        'paginator': paginator,
        'institutions': institutions,
        'accreditation_bodies': accreditation_bodies,
        'accreditation_statuses': AccreditationStatus.choices,
        'filter_institution': filter_institution,
        'filter_status': filter_status,
        'filter_accreditation_body': filter_accreditation_body,
    }
    html_template = loader.get_template('super-admin/global-accreditation/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@csrf_exempt
def accreditation_record_create(request):
    """Create a new accreditation record"""
    if request.user.role != 'super_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        from apps.institutions.models import AccreditationRecord
        import json
        
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
            
            # Validate required fields
            if not data.get('institution'):
                return JsonResponse({'error': 'Institution is required'}, status=400)
            if not data.get('accreditation_body'):
                return JsonResponse({'error': 'Accreditation body is required'}, status=400)
            if not data.get('status'):
                return JsonResponse({'error': 'Status is required'}, status=400)
            if not data.get('granted_date'):
                return JsonResponse({'error': 'Granted date is required'}, status=400)
            
            # Get institution
            try:
                from apps.institutions.models import Institution
                institution = Institution.objects.get(id=data.get('institution'))
            except Institution.DoesNotExist:
                return JsonResponse({'error': 'Institution not found'}, status=400)
            
            # Create accreditation record
            accreditation_record = AccreditationRecord.objects.create(
                institution=institution,
                accreditation_body=data.get('accreditation_body', ''),
                status=data.get('status', ''),
                granted_date=data.get('granted_date'),
                expiry_date=data.get('expiry_date') or None,
                certificate_number=data.get('certificate_number', ''),
                notes=data.get('notes', ''),
            )
            
            # Handle certificate document upload
            if 'certificate_document' in request.FILES:
                accreditation_record.certificate_document = request.FILES['certificate_document']
                accreditation_record.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Accreditation record created successfully',
                'accreditation_record': {
                    'id': str(accreditation_record.id),
                    'institution': institution.name,
                    'accreditation_body': accreditation_record.accreditation_body,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def accreditation_record_update(request, record_id):
    """Update an accreditation record"""
    if request.user.role != 'super_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    from apps.institutions.models import AccreditationRecord
    import uuid
    
    try:
        accreditation_record = AccreditationRecord.objects.get(id=uuid.UUID(str(record_id)))
    except AccreditationRecord.DoesNotExist:
        return JsonResponse({'error': 'Accreditation record not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid accreditation record ID'}, status=400)
    
    if request.method in ['POST', 'PUT', 'PATCH']:
        import json
        
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
            
            # Validate required fields
            if not data.get('accreditation_body'):
                return JsonResponse({'error': 'Accreditation body is required'}, status=400)
            if not data.get('status'):
                return JsonResponse({'error': 'Status is required'}, status=400)
            if not data.get('granted_date'):
                return JsonResponse({'error': 'Granted date is required'}, status=400)
            
            # Update institution if provided
            if data.get('institution'):
                try:
                    from apps.institutions.models import Institution
                    institution = Institution.objects.get(id=data.get('institution'))
                    accreditation_record.institution = institution
                except Institution.DoesNotExist:
                    return JsonResponse({'error': 'Institution not found'}, status=400)
            
            # Update fields
            accreditation_record.accreditation_body = data.get('accreditation_body', accreditation_record.accreditation_body)
            accreditation_record.status = data.get('status', accreditation_record.status)
            accreditation_record.granted_date = data.get('granted_date', accreditation_record.granted_date)
            accreditation_record.expiry_date = data.get('expiry_date') or accreditation_record.expiry_date
            accreditation_record.certificate_number = data.get('certificate_number', accreditation_record.certificate_number)
            accreditation_record.notes = data.get('notes', accreditation_record.notes)
            
            # Handle certificate document upload
            if 'certificate_document' in request.FILES:
                accreditation_record.certificate_document = request.FILES['certificate_document']
            
            accreditation_record.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Accreditation record updated successfully',
                'accreditation_record': {
                    'id': str(accreditation_record.id),
                    'institution': accreditation_record.institution.name,
                    'accreditation_body': accreditation_record.accreditation_body,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def accreditation_record_delete(request, record_id):
    """Delete an accreditation record"""
    if request.user.role != 'super_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    from apps.institutions.models import AccreditationRecord
    import uuid
    
    try:
        accreditation_record = AccreditationRecord.objects.get(id=uuid.UUID(str(record_id)))
    except AccreditationRecord.DoesNotExist:
        return JsonResponse({'error': 'Accreditation record not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid accreditation record ID'}, status=400)
    
    if request.method == 'POST' or request.method == 'DELETE':
        try:
            record_info = f"{accreditation_record.institution.name} - {accreditation_record.accreditation_body}"
            accreditation_record.delete()
            return JsonResponse({
                'success': True,
                'message': f'Accreditation record "{record_info}" deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def accreditation_record_detail(request, record_id):
    """Get accreditation record details"""
    if request.user.role != 'super_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    from apps.institutions.models import AccreditationRecord
    import uuid
    
    try:
        accreditation_record = AccreditationRecord.objects.get(id=uuid.UUID(str(record_id)))
    except AccreditationRecord.DoesNotExist:
        return JsonResponse({'error': 'Accreditation record not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid accreditation record ID'}, status=400)
    
    if request.method == 'GET':
        return JsonResponse({
            'id': str(accreditation_record.id),
            'institution': str(accreditation_record.institution.id),
            'institution_name': accreditation_record.institution.name,
            'accreditation_body': accreditation_record.accreditation_body,
            'status': accreditation_record.status,
            'granted_date': accreditation_record.granted_date.isoformat() if accreditation_record.granted_date else None,
            'expiry_date': accreditation_record.expiry_date.isoformat() if accreditation_record.expiry_date else None,
            'certificate_number': accreditation_record.certificate_number,
            'notes': accreditation_record.notes,
            'certificate_document': accreditation_record.certificate_document.url if accreditation_record.certificate_document else None,
            'created_at': accreditation_record.created_at.isoformat() if accreditation_record.created_at else None,
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
def super_admin_ledger(request):
    """Super Admin - Credentials Ledger"""
    if request.user.role != 'super_admin':
        return redirect('dashboard')
    
    from apps.credentials.models import Credential, CredentialStatus, CredentialType, BlockchainTransaction
    from apps.institutions.models import Institution
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.db.models import Q
    
    # Get search query and filters
    search_query = request.GET.get('search', '').strip()
    filter_status = request.GET.get('status', '')
    filter_type = request.GET.get('type', '')
    filter_institution = request.GET.get('institution', '')
    filter_has_blockchain = request.GET.get('has_blockchain', '')
    
    # Fetch all credentials with related data
    credentials = Credential.objects.select_related(
        'holder', 'institution', 'program', 'issued_by'
    ).prefetch_related('blockchain_transactions').order_by('-created_at')
    
    # Apply search filter if query exists
    if search_query:
        credentials = credentials.filter(
            Q(credential_id__icontains=search_query) |
            Q(holder_name__icontains=search_query) |
            Q(holder__email__icontains=search_query) |
            Q(holder_student_id__icontains=search_query) |
            Q(program_name__icontains=search_query) |
            Q(blockchain_hash__icontains=search_query) |
            Q(blockchain_tx_id__icontains=search_query) |
            Q(institution__name__icontains=search_query)
        )
    
    # Apply filters
    if filter_status:
        credentials = credentials.filter(status=filter_status)
    if filter_type:
        credentials = credentials.filter(credential_type=filter_type)
    if filter_institution:
        credentials = credentials.filter(institution_id=filter_institution)
    if filter_has_blockchain:
        if filter_has_blockchain == 'yes':
            credentials = credentials.exclude(blockchain_hash='')
        elif filter_has_blockchain == 'no':
            credentials = credentials.filter(blockchain_hash='')
    
    # Pagination - 20 items per page
    paginator = Paginator(credentials, 20)
    page = request.GET.get('page', 1)
    
    try:
        credentials_page = paginator.page(page)
    except PageNotAnInteger:
        credentials_page = paginator.page(1)
    except EmptyPage:
        credentials_page = paginator.page(paginator.num_pages)
    
    # Get all institutions for filter dropdown
    institutions = Institution.objects.all().order_by('name')
    
    # Calculate statistics
    total_credentials = Credential.objects.count()
    issued_credentials = Credential.objects.filter(status=CredentialStatus.ISSUED).count()
    revoked_credentials = Credential.objects.filter(status=CredentialStatus.REVOKED).count()
    blockchain_credentials = Credential.objects.exclude(blockchain_hash='').count()
    
    # Get latest blockchain transactions
    latest_transactions = BlockchainTransaction.objects.select_related('credential').order_by('-created_at')[:10]
    
    context = {
        'segment': 'ledger',
        'user': request.user,
        'credentials': credentials_page,
        'search_query': search_query,
        'paginator': paginator,
        'institutions': institutions,
        'credential_statuses': CredentialStatus.choices,
        'credential_types': CredentialType.choices,
        'filter_status': filter_status,
        'filter_type': filter_type,
        'filter_institution': filter_institution,
        'filter_has_blockchain': filter_has_blockchain,
        'total_credentials': total_credentials,
        'issued_credentials': issued_credentials,
        'revoked_credentials': revoked_credentials,
        'blockchain_credentials': blockchain_credentials,
        'latest_transactions': latest_transactions,
    }
    html_template = loader.get_template('super-admin/credentials-ledger/index.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def super_admin_analytics(request):
    """Super Admin - Analytics"""
    if request.user.role != 'super_admin':
        return redirect('dashboard')
    
    from apps.credentials.models import Credential, CredentialStatus, CredentialType, BlockchainTransaction
    from apps.verifications.models import VerificationLog, VerificationResult, VerificationMethod
    from apps.institutions.models import Institution, AccreditationRecord
    from apps.accounts.models import User, UserRole
    from django.db.models import Count, Q, Avg, Sum
    from django.utils import timezone
    from datetime import timedelta, datetime
    import json
    
    # Date ranges
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)
    
    # Overview Statistics
    total_credentials = Credential.objects.count()
    issued_credentials = Credential.objects.filter(status=CredentialStatus.ISSUED).count()
    revoked_credentials = Credential.objects.filter(status=CredentialStatus.REVOKED).count()
    blockchain_credentials = Credential.objects.exclude(blockchain_hash='').count()
    
    total_verifications = VerificationLog.objects.count()
    valid_verifications = VerificationLog.objects.filter(result=VerificationResult.VALID).count()
    invalid_verifications = VerificationLog.objects.filter(result=VerificationResult.INVALID).count()
    revoked_verifications = VerificationLog.objects.filter(result=VerificationResult.REVOKED).count()
    
    total_institutions = Institution.objects.count()
    active_institutions = Institution.objects.filter(is_active=True).count()
    partner_institutions = Institution.objects.filter(is_partner=True).count()
    
    total_users = User.objects.count()
    students = User.objects.filter(role=UserRole.STUDENT).count()
    institution_admins = User.objects.filter(role=UserRole.INSTITUTION_ADMIN).count()
    employers = User.objects.filter(role=UserRole.EMPLOYER).count()
    
    # Today's statistics
    credentials_today = Credential.objects.filter(created_at__date=today).count()
    verifications_today = VerificationLog.objects.filter(created_at__date=today).count()
    users_today = User.objects.filter(date_joined__date=today).count()
    
    # This week's statistics
    credentials_this_week = Credential.objects.filter(created_at__gte=week_ago).count()
    verifications_this_week = VerificationLog.objects.filter(created_at__gte=week_ago).count()
    users_this_week = User.objects.filter(date_joined__gte=week_ago).count()
    
    # This month's statistics
    credentials_this_month = Credential.objects.filter(created_at__gte=month_ago).count()
    verifications_this_month = VerificationLog.objects.filter(created_at__gte=month_ago).count()
    users_this_month = User.objects.filter(date_joined__gte=month_ago).count()
    
    # Credential trends (last 30 days)
    credential_trends = []
    verification_trends = []
    dates = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        dates.append(date.strftime('%m/%d'))
        credential_trends.append(
            Credential.objects.filter(created_at__date=date).count()
        )
        verification_trends.append(
            VerificationLog.objects.filter(created_at__date=date).count()
        )
    
    # Credentials by status
    credentials_by_status = {
        'issued': Credential.objects.filter(status=CredentialStatus.ISSUED).count(),
        'pending': Credential.objects.filter(status=CredentialStatus.PENDING).count(),
        'revoked': Credential.objects.filter(status=CredentialStatus.REVOKED).count(),
        'expired': Credential.objects.filter(status=CredentialStatus.EXPIRED).count(),
        'draft': Credential.objects.filter(status=CredentialStatus.DRAFT).count(),
    }
    
    # Credentials by type
    credentials_by_type = {}
    for value, label in CredentialType.choices:
        credentials_by_type[label] = Credential.objects.filter(credential_type=value).count()
    
    # Verifications by result
    verifications_by_result = {
        'valid': VerificationLog.objects.filter(result=VerificationResult.VALID).count(),
        'invalid': VerificationLog.objects.filter(result=VerificationResult.INVALID).count(),
        'revoked': VerificationLog.objects.filter(result=VerificationResult.REVOKED).count(),
        'expired': VerificationLog.objects.filter(result=VerificationResult.EXPIRED).count(),
        'not_found': VerificationLog.objects.filter(result=VerificationResult.NOT_FOUND).count(),
        'error': VerificationLog.objects.filter(result=VerificationResult.ERROR).count(),
    }
    
    # Verifications by method
    verifications_by_method = {}
    for value, label in VerificationMethod.choices:
        verifications_by_method[label] = VerificationLog.objects.filter(method=value).count()
    
    # Top institutions by credentials issued
    top_institutions = Institution.objects.annotate(
        credential_count=Count('credentials')
    ).order_by('-credential_count')[:10]
    
    # Top verifiers
    top_verifiers = User.objects.filter(
        role=UserRole.EMPLOYER
    ).annotate(
        verification_count=Count('verifications_performed')
    ).order_by('-verification_count')[:10]
    
    # Average response time
    avg_response_time = VerificationLog.objects.aggregate(
        avg_time=Avg('response_time_ms')
    )['avg_time'] or 0
    
    # Blockchain statistics
    total_transactions = BlockchainTransaction.objects.count()
    confirmed_transactions = BlockchainTransaction.objects.filter(is_confirmed=True).count()
    pending_transactions = BlockchainTransaction.objects.filter(is_confirmed=False).count()
    
    # Calculate blockchain percentage
    blockchain_percentage = 0
    if total_credentials > 0:
        blockchain_percentage = round((blockchain_credentials / total_credentials) * 100, 1)
    
    context = {
        'segment': 'analytics',
        'user': request.user,
        # Overview stats
        'total_credentials': total_credentials,
        'issued_credentials': issued_credentials,
        'revoked_credentials': revoked_credentials,
        'blockchain_credentials': blockchain_credentials,
        'total_verifications': total_verifications,
        'valid_verifications': valid_verifications,
        'invalid_verifications': invalid_verifications,
        'revoked_verifications': revoked_verifications,
        'total_institutions': total_institutions,
        'active_institutions': active_institutions,
        'partner_institutions': partner_institutions,
        'total_users': total_users,
        'students': students,
        'institution_admins': institution_admins,
        'employers': employers,
        # Today's stats
        'credentials_today': credentials_today,
        'verifications_today': verifications_today,
        'users_today': users_today,
        # This week's stats
        'credentials_this_week': credentials_this_week,
        'verifications_this_week': verifications_this_week,
        'users_this_week': users_this_week,
        # This month's stats
        'credentials_this_month': credentials_this_month,
        'verifications_this_month': verifications_this_month,
        'users_this_month': users_this_month,
        # Trends data (JSON for JavaScript)
        'credential_trends': json.dumps(credential_trends),
        'verification_trends': json.dumps(verification_trends),
        'trend_dates': json.dumps(dates),
        # Breakdown data
        'credentials_by_status': json.dumps(credentials_by_status),
        'credentials_by_type': json.dumps(credentials_by_type),
        'verifications_by_result': json.dumps(verifications_by_result),
        'verifications_by_method': json.dumps(verifications_by_method),
        # Top lists
        'top_institutions': top_institutions,
        'top_verifiers': top_verifiers,
        # Other stats
        'avg_response_time': round(avg_response_time, 2) if avg_response_time else 0,
        'total_transactions': total_transactions,
        'confirmed_transactions': confirmed_transactions,
        'pending_transactions': pending_transactions,
        'blockchain_percentage': blockchain_percentage,
    }
    html_template = loader.get_template('super-admin/analytics/index.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def super_admin_settings(request):
    """Super Admin - Settings"""
    if request.user.role != 'super_admin':
        return redirect('dashboard')
    
    from apps.home.models import GeneralSettings
    from apps.home.forms import GeneralSettingsForm
    
    # Get or create settings instance (singleton pattern)
    settings_instance, created = GeneralSettings.objects.get_or_create(
        pk=1,
        defaults={
            'site_name': 'CertChain',
            'site_name_abb': 'CC',
            'slogan': 'Blockchain-Verified Academic Credentials',
        }
    )
    
    if request.method == 'POST':
        form = GeneralSettingsForm(request.POST, request.FILES, instance=settings_instance)
        if form.is_valid():
            try:
                form.save()
                # Return success response for AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Settings updated successfully'
                    })
                # For regular form submission, redirect with success message
                return redirect('super_admin_settings')
            except Exception as e:
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error saving GeneralSettings: {str(e)}", exc_info=True)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Error saving settings: {str(e)}',
                        'errors': {}
                    }, status=500)
                # For regular form submission, show error
                from django.contrib import messages
                messages.error(request, f'Error saving settings: {str(e)}')
                return redirect('super_admin_settings')
        else:
            # Log form errors for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Form validation errors: {form.errors}")
            
            # Return error response for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Format errors for better display
                error_dict = {}
                for field, errors in form.errors.items():
                    error_dict[field] = [str(error) for error in errors]
                
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the errors below',
                    'errors': error_dict
                }, status=400)
    else:
        form = GeneralSettingsForm(instance=settings_instance)
    
    context = {
        'segment': 'settings',
        'user': request.user,
        'settings': settings_instance,
        'form': form,
    }
    html_template = loader.get_template('super-admin/settings/index.html')
    return HttpResponse(html_template.render(context, request))


# ============================================================================
# INSTITUTION ADMIN VIEWS
# ============================================================================

@login_required(login_url="/login/")
def institution_admin_dashboard(request):
    """Institution Admin Dashboard"""
    if request.user.role != 'institution_admin':
        return redirect('dashboard')
    
    context = {
        'segment': 'inst-dashboard',
        'user': request.user,
    }
    html_template = loader.get_template('dashboard.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def institution_admin_issue_credentials(request):
    """Institution Admin - Issue Credentials"""
    if request.user.role != 'institution_admin':
        return redirect('dashboard')

    from apps.credentials.models import Credential, CredentialType, CredentialStatus
    from apps.institutions.models import Program
    from apps.accounts.models import User, UserRole, InstitutionAdminProfile, StudentProfile
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.db.models import Q
    
    # Get institution from admin profile - REQUIRED
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        # If no profile exists, redirect to dashboard
        return redirect('dashboard')
    
    # Get search query and filters
    search_query = request.GET.get('search', '').strip()
    filter_type = request.GET.get('type', '')
    filter_status = request.GET.get('status', '')
    
    # Fetch credentials for this institution ONLY
    credentials = Credential.objects.filter(institution=institution).order_by('-created_at')
    
    # Apply search filter if query exists (maintain institution filter)
    if search_query:
        credentials = credentials.filter(
            Q(credential_id__icontains=search_query) |
            Q(holder_name__icontains=search_query) |
            Q(holder_student_id__icontains=search_query) |
            Q(program_name__icontains=search_query) |
            Q(holder__email__icontains=search_query)
        )
    
    # Apply filters (maintain institution filter)
    if filter_type:
        credentials = credentials.filter(credential_type=filter_type)
    if filter_status:
        credentials = credentials.filter(status=filter_status)
    
    # Pagination - 20 items per page
    paginator = Paginator(credentials, 20)
    page = request.GET.get('page', 1)
    
    try:
        credentials_page = paginator.page(page)
    except PageNotAnInteger:
        credentials_page = paginator.page(1)
    except EmptyPage:
        credentials_page = paginator.page(paginator.num_pages)
    
    # Get programs for this institution ONLY
    programs = Program.objects.filter(institution=institution, is_active=True).order_by('name')
    
    # Get students from this institution ONLY
    # Use StudentProfile to ensure we only get students from this institution
    students = User.objects.filter(
        role=UserRole.STUDENT,
        student_profile__institution=institution
    ).select_related('student_profile').distinct().order_by('first_name', 'last_name')
    
    context = {
        'segment': 'issue-credentials',
        'user': request.user,
        'credentials': credentials_page,
        'search_query': search_query,
        'paginator': paginator,
        'credential_types': CredentialType.choices,
        'credential_statuses': CredentialStatus.choices,
        'programs': programs,
        'students': students,
        'institution': institution,
        'filter_type': filter_type,
        'filter_status': filter_status,
    }
    html_template = loader.get_template('institution-admin/issue-credentials/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@csrf_exempt
def credential_create(request):
    """Create a new credential"""
    if request.user.role != 'institution_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get institution from admin profile
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        return JsonResponse({'error': 'No institution associated with your account'}, status=400)
    
    if request.method == 'POST':
        from apps.credentials.models import Credential, CredentialType, CredentialStatus
        from apps.institutions.models import Program
        import json
        from django.utils import timezone
        
        try:
            # Handle both JSON, form data, and multipart/form-data (with files)
            data = {}
            document_file = None
            
            if 'multipart/form-data' in request.content_type or request.FILES:
                # Handle multipart/form-data (file upload)
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
                # Get uploaded file if present
                if 'document' in request.FILES:
                    document_file = request.FILES['document']
                    # Validate file size (10MB max)
                    if document_file.size > 10 * 1024 * 1024:
                        return JsonResponse({'error': 'File size must be less than 10MB'}, status=400)
            elif request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
            
            # Validate required fields
            if not data.get('holder'):
                return JsonResponse({'error': 'Student is required'}, status=400)
            if not data.get('holder_name'):
                return JsonResponse({'error': 'Holder name is required'}, status=400)
            if not data.get('program_name'):
                return JsonResponse({'error': 'Program name is required'}, status=400)
            
            # Get holder user and verify they belong to this institution
            try:
                holder = User.objects.get(id=data.get('holder'), role='student')
                # Verify the student belongs to this institution
                from apps.accounts.models import StudentProfile
                try:
                    student_profile = StudentProfile.objects.get(user=holder, institution=institution)
                except StudentProfile.DoesNotExist:
                    return JsonResponse({'error': 'Student does not belong to your institution'}, status=403)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Student not found'}, status=400)
            
            # Get program if provided - must belong to this institution
            program = None
            if data.get('program'):
                try:
                    program = Program.objects.get(id=data.get('program'), institution=institution)
                except Program.DoesNotExist:
                    return JsonResponse({'error': 'Program does not belong to your institution'}, status=403)
            
            # Create credential
            credential = Credential.objects.create(
                credential_type=data.get('credential_type', CredentialType.DEGREE),
                holder=holder,
                holder_name=data.get('holder_name', ''),
                holder_student_id=data.get('holder_student_id', ''),
                holder_date_of_birth=data.get('holder_date_of_birth') or None,
                institution=institution,
                program=program,
                program_name=data.get('program_name', ''),
                degree_level=data.get('degree_level', ''),
                major=data.get('major', ''),
                minor=data.get('minor', ''),
                specialization=data.get('specialization', ''),
                grade=data.get('grade', ''),
                honors=data.get('honors', ''),
                credits_earned=float(data.get('credits_earned', 0)) if data.get('credits_earned') else None,
                enrollment_date=data.get('enrollment_date') or None,
                completion_date=data.get('completion_date') or None,
                issue_date=data.get('issue_date') or timezone.now().date(),
                expiry_date=data.get('expiry_date') or None,
                status=data.get('status', CredentialStatus.ISSUED),
                issued_by=request.user,
                notes=data.get('notes', ''),
            )
            
            # Handle document file upload if present
            if document_file:
                credential.document = document_file
                # Calculate document hash
                import hashlib
                document_file.seek(0)  # Reset file pointer
                file_content = document_file.read()
                credential.document_hash = hashlib.sha256(file_content).hexdigest()
                document_file.seek(0)  # Reset again for saving
                credential.save(update_fields=['document', 'document_hash'])
            
            return JsonResponse({
                'success': True,
                'message': 'Credential issued successfully',
                'credential': {
                    'id': str(credential.id),
                    'credential_id': credential.credential_id,
                    'holder_name': credential.holder_name,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def credential_update(request, credential_id):
    """Update a credential"""
    if request.user.role != 'institution_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get institution from admin profile
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        return JsonResponse({'error': 'No institution associated with your account'}, status=400)
    
    from apps.credentials.models import Credential
    from apps.institutions.models import Program
    import uuid
    
    try:
        credential = Credential.objects.get(id=uuid.UUID(str(credential_id)), institution=institution)
    except Credential.DoesNotExist:
        return JsonResponse({'error': 'Credential not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid credential ID'}, status=400)
    
    # Prevent editing issued/revoked credentials
    if credential.status in ['issued', 'revoked']:
        return JsonResponse({'error': 'Cannot edit issued or revoked credentials'}, status=403)
    
    if request.method in ['POST', 'PUT', 'PATCH']:
        import json
        
        try:
            # Handle both JSON, form data, and multipart/form-data (with files)
            data = {}
            document_file = None
            
            if 'multipart/form-data' in request.content_type or request.FILES:
                # Handle multipart/form-data (file upload)
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
                # Get uploaded file if present
                if 'document' in request.FILES:
                    document_file = request.FILES['document']
                    # Validate file size (10MB max)
                    if document_file.size > 10 * 1024 * 1024:
                        return JsonResponse({'error': 'File size must be less than 10MB'}, status=400)
            elif request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
            
            # Update credential fields
            if data.get('holder'):
                try:
                    new_holder = User.objects.get(id=data.get('holder'), role='student')
                    # Verify the student belongs to this institution
                    from apps.accounts.models import StudentProfile
                    try:
                        student_profile = StudentProfile.objects.get(user=new_holder, institution=institution)
                        credential.holder = new_holder
                    except StudentProfile.DoesNotExist:
                        return JsonResponse({'error': 'Student does not belong to your institution'}, status=403)
                except User.DoesNotExist:
                    return JsonResponse({'error': 'Student not found'}, status=400)
            
            credential.holder_name = data.get('holder_name', credential.holder_name)
            credential.holder_student_id = data.get('holder_student_id', credential.holder_student_id)
            credential.holder_date_of_birth = data.get('holder_date_of_birth') or credential.holder_date_of_birth
            
            if data.get('program'):
                try:
                    credential.program = Program.objects.get(id=data.get('program'), institution=institution)
                except Program.DoesNotExist:
                    credential.program = None
            
            credential.program_name = data.get('program_name', credential.program_name)
            credential.degree_level = data.get('degree_level', credential.degree_level)
            credential.major = data.get('major', credential.major)
            credential.minor = data.get('minor', credential.minor)
            credential.specialization = data.get('specialization', credential.specialization)
            credential.grade = data.get('grade', credential.grade)
            credential.honors = data.get('honors', credential.honors)
            if data.get('credits_earned'):
                credential.credits_earned = float(data.get('credits_earned'))
            
            credential.enrollment_date = data.get('enrollment_date') or credential.enrollment_date
            credential.completion_date = data.get('completion_date') or credential.completion_date
            credential.issue_date = data.get('issue_date') or credential.issue_date
            credential.expiry_date = data.get('expiry_date') or credential.expiry_date
            credential.notes = data.get('notes', credential.notes)
            
            credential.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Credential updated successfully',
                'credential': {
                    'id': str(credential.id),
                    'credential_id': credential.credential_id,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def credential_delete(request, credential_id):
    """Delete a credential"""
    if request.user.role != 'institution_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get institution from admin profile
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        return JsonResponse({'error': 'No institution associated with your account'}, status=400)
    
    from apps.credentials.models import Credential
    import uuid
    
    try:
        credential = Credential.objects.get(id=uuid.UUID(str(credential_id)), institution=institution)
    except Credential.DoesNotExist:
        return JsonResponse({'error': 'Credential not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid credential ID'}, status=400)
    
    # Only allow deleting draft credentials
    if credential.status != 'draft':
        return JsonResponse({'error': 'Can only delete draft credentials'}, status=403)
    
    if request.method == 'POST' or request.method == 'DELETE':
        try:
            credential_id_str = credential.credential_id
            credential.delete()
            return JsonResponse({
                'success': True,
                'message': f'Credential "{credential_id_str}" deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
def credential_detail(request, credential_id):
    """Get credential details"""
    if request.user.role != 'institution_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get institution from admin profile
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        return JsonResponse({'error': 'No institution associated with your account'}, status=400)
    
    from apps.credentials.models import Credential
    import uuid
    
    try:
        credential = Credential.objects.get(id=uuid.UUID(str(credential_id)), institution=institution)
    except Credential.DoesNotExist:
        return JsonResponse({'error': 'Credential not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid credential ID'}, status=400)
    
    if request.method == 'GET':
        return JsonResponse({
            'id': str(credential.id),
            'credential_id': credential.credential_id,
            'credential_type': credential.credential_type,
            'status': credential.status,
            'holder': str(credential.holder.id),
            'holder_name': credential.holder_name,
            'holder_student_id': credential.holder_student_id,
            'holder_date_of_birth': credential.holder_date_of_birth.isoformat() if credential.holder_date_of_birth else None,
            'program': str(credential.program.id) if credential.program else None,
            'program_name': credential.program_name,
            'degree_level': credential.degree_level,
            'major': credential.major,
            'minor': credential.minor,
            'specialization': credential.specialization,
            'grade': credential.grade,
            'honors': credential.honors,
            'credits_earned': float(credential.credits_earned) if credential.credits_earned else None,
            'enrollment_date': credential.enrollment_date.isoformat() if credential.enrollment_date else None,
            'completion_date': credential.completion_date.isoformat() if credential.completion_date else None,
            'issue_date': credential.issue_date.isoformat() if credential.issue_date else None,
            'expiry_date': credential.expiry_date.isoformat() if credential.expiry_date else None,
            'notes': credential.notes,
            'document': credential.document.url if credential.document else None,
            'document_name': credential.document.name.split('/')[-1] if credential.document else None,
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
def institution_admin_students(request):
    """Institution Admin - Students Management"""
    if request.user.role != 'institution_admin':
        return redirect('dashboard')
    
    from apps.accounts.models import StudentProfile, UserRole, InstitutionAdminProfile
    from apps.institutions.models import Program
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.db.models import Q
    
    # Get institution from admin profile - REQUIRED
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        # If no profile exists, redirect to dashboard with error message
        return redirect('dashboard')
    
    # Get search query and filters
    search_query = request.GET.get('search', '').strip()
    filter_program = request.GET.get('program', '')
    filter_status = request.GET.get('status', '')  # 'active', 'inactive'
    filter_verified = request.GET.get('verified', '')  # 'true', 'false'
    
    # Fetch students for this institution ONLY
    # Use StudentProfile to ensure we only get students from this institution
    students = User.objects.filter(
        role=UserRole.STUDENT,
        student_profile__institution=institution
    ).select_related('student_profile').distinct().order_by('-date_joined')
    
    # Apply search filter if query exists (maintain institution filter)
    if search_query:
        students = students.filter(
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_profile__student_id__icontains=search_query)
        )
    
    # Apply program filter (maintain institution filter)
    if filter_program:
        students = students.filter(student_profile__program__icontains=filter_program)
    
    # Apply status filter
    if filter_status:
        students = students.filter(is_active=_parse_bool(filter_status))
    
    # Apply verified filter
    if filter_verified:
        students = students.filter(is_verified=_parse_bool(filter_verified))
    
    # Pagination - 20 items per page
    paginator = Paginator(students, 20)
    page = request.GET.get('page', 1)
    
    try:
        students_page = paginator.page(page)
    except PageNotAnInteger:
        students_page = paginator.page(1)
    except EmptyPage:
        students_page = paginator.page(paginator.num_pages)
    
    # Get programs for this institution ONLY
    programs = Program.objects.filter(institution=institution, is_active=True).order_by('name')
    
    # Get unique programs from student profiles for filter (this institution only)
    student_programs = StudentProfile.objects.filter(
        institution=institution
    ).exclude(program='').values_list('program', flat=True).distinct().order_by('program')
    
    # Get program names from Program model to check against student_programs
    program_names = list(programs.values_list('name', flat=True))
    
    context = {
        'segment': 'students',
        'user': request.user,
        'students': students_page,
        'search_query': search_query,
        'paginator': paginator,
        'programs': programs,
        'program_names': program_names,
        'student_programs': student_programs,
        'institution': institution,
        'filter_program': filter_program,
        'filter_status': filter_status,
        'filter_verified': filter_verified,
    }
    html_template = loader.get_template('institution-admin/students/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@csrf_exempt
def student_create(request):
    """Create a new student"""
    if request.user.role != 'institution_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get institution from admin profile
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        return JsonResponse({'error': 'No institution associated with your account'}, status=400)
    
    if request.method == 'POST':
        from apps.accounts.models import StudentProfile, UserRole
        import json
        
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
            
            # Validate required fields
            if not data.get('email'):
                return JsonResponse({'error': 'Email is required'}, status=400)
            if not data.get('first_name'):
                return JsonResponse({'error': 'First name is required'}, status=400)
            if not data.get('last_name'):
                return JsonResponse({'error': 'Last name is required'}, status=400)
            
            # Check if user already exists
            if User.objects.filter(email=data.get('email')).exists():
                return JsonResponse({'error': 'User with this email already exists'}, status=400)
            
            # Create user
            user = User.objects.create_user(
                email=data.get('email'),
                password=data.get('password', 'Student@123'),  # Default password
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                phone=data.get('phone', ''),
                role=UserRole.STUDENT,
                is_active=_parse_bool(data.get('is_active', True)),
                is_verified=_parse_bool(data.get('is_verified', False)),
            )
            
            # Create student profile
            student_profile, created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'institution': institution,
                    'student_id': data.get('student_id', ''),
                    'date_of_birth': data.get('date_of_birth') or None,
                    'nationality': data.get('nationality', ''),
                    'address': data.get('address', ''),
                    'program': data.get('program', ''),
                    'enrollment_date': data.get('enrollment_date') or None,
                    'graduation_date': data.get('graduation_date') or None,
                }
            )
            
            if not created:
                # Update existing profile
                student_profile.institution = institution
                student_profile.student_id = data.get('student_id', student_profile.student_id)
                student_profile.date_of_birth = data.get('date_of_birth') or student_profile.date_of_birth
                student_profile.nationality = data.get('nationality', student_profile.nationality)
                student_profile.address = data.get('address', student_profile.address)
                student_profile.program = data.get('program', student_profile.program)
                student_profile.enrollment_date = data.get('enrollment_date') or student_profile.enrollment_date
                student_profile.graduation_date = data.get('graduation_date') or student_profile.graduation_date
                student_profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Student created successfully',
                'student': {
                    'id': str(user.id),
                    'email': user.email,
                    'full_name': user.full_name,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def student_update(request, student_id):
    """Update a student"""
    if request.user.role != 'institution_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get institution from admin profile
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        return JsonResponse({'error': 'No institution associated with your account'}, status=400)
    
    from apps.accounts.models import StudentProfile
    import uuid
    
    try:
        user = User.objects.get(id=uuid.UUID(str(student_id)), role='student')
        student_profile = StudentProfile.objects.get(user=user, institution=institution)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except StudentProfile.DoesNotExist:
        return JsonResponse({'error': 'Student profile not found for this institution'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid student ID'}, status=400)
    
    if request.method in ['POST', 'PUT', 'PATCH']:
        import json
        
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
            
            # Update user fields
            if data.get('email') and data.get('email') != user.email:
                if User.objects.filter(email=data.get('email')).exclude(id=user.id).exists():
                    return JsonResponse({'error': 'Email already in use'}, status=400)
                user.email = data.get('email')
            
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.phone = data.get('phone', user.phone)
            user.is_active = _parse_bool(data.get('is_active', user.is_active))
            user.is_verified = _parse_bool(data.get('is_verified', user.is_verified))
            
            # Update password if provided
            if data.get('password'):
                user.set_password(data.get('password'))
            
            user.save()
            
            # Update student profile
            student_profile.student_id = data.get('student_id', student_profile.student_id)
            student_profile.date_of_birth = data.get('date_of_birth') or student_profile.date_of_birth
            student_profile.nationality = data.get('nationality', student_profile.nationality)
            student_profile.address = data.get('address', student_profile.address)
            student_profile.program = data.get('program', student_profile.program)
            student_profile.enrollment_date = data.get('enrollment_date') or student_profile.enrollment_date
            student_profile.graduation_date = data.get('graduation_date') or student_profile.graduation_date
            student_profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Student updated successfully',
                'student': {
                    'id': str(user.id),
                    'email': user.email,
                    'full_name': user.full_name,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def student_delete(request, student_id):
    """Delete a student"""
    if request.user.role != 'institution_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get institution from admin profile
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        return JsonResponse({'error': 'No institution associated with your account'}, status=400)
    
    from apps.accounts.models import StudentProfile
    import uuid
    
    try:
        user = User.objects.get(id=uuid.UUID(str(student_id)), role='student')
        student_profile = StudentProfile.objects.get(user=user, institution=institution)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except StudentProfile.DoesNotExist:
        return JsonResponse({'error': 'Student profile not found for this institution'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid student ID'}, status=400)
    
    if request.method == 'POST' or request.method == 'DELETE':
        try:
            student_email = user.email
            user.delete()  # This will cascade delete the student profile
            return JsonResponse({
                'success': True,
                'message': f'Student "{student_email}" deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
def student_detail(request, student_id):
    """Get student details"""
    if request.user.role != 'institution_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get institution from admin profile
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        return JsonResponse({'error': 'No institution associated with your account'}, status=400)
    
    from apps.accounts.models import StudentProfile
    import uuid
    
    try:
        user = User.objects.get(id=uuid.UUID(str(student_id)), role='student')
        student_profile = StudentProfile.objects.get(user=user, institution=institution)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except StudentProfile.DoesNotExist:
        return JsonResponse({'error': 'Student profile not found for this institution'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid student ID'}, status=400)
    
    if request.method == 'GET':
        return JsonResponse({
            'id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'phone': user.phone,
            'is_active': user.is_active,
            'is_verified': user.is_verified,
            'avatar': user.avatar.url if user.avatar else None,
            'student_id': student_profile.student_id,
            'date_of_birth': student_profile.date_of_birth.isoformat() if student_profile.date_of_birth else None,
            'nationality': student_profile.nationality,
            'address': student_profile.address,
            'program': student_profile.program,
            'enrollment_date': student_profile.enrollment_date.isoformat() if student_profile.enrollment_date else None,
            'graduation_date': student_profile.graduation_date.isoformat() if student_profile.graduation_date else None,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
def institution_admin_verification_logs(request):
    """Institution Admin - Verification Logs"""
    if request.user.role != 'institution_admin':
        return redirect('dashboard')
    
    from apps.verifications.models import VerificationLog, VerificationMethod, VerificationResult
    from apps.accounts.models import InstitutionAdminProfile
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.db.models import Q
    
    # Get institution from admin profile - REQUIRED
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        # If no profile exists, redirect to dashboard
        return redirect('dashboard')
    
    # Get search query and filters
    search_query = request.GET.get('search', '').strip()
    filter_method = request.GET.get('method', '')
    filter_result = request.GET.get('result', '')
    filter_date_from = request.GET.get('date_from', '')
    filter_date_to = request.GET.get('date_to', '')
    
    # Fetch verification logs for credentials from this institution ONLY
    verification_logs = VerificationLog.objects.filter(
        credential__institution=institution
    ).select_related('credential', 'verifier', 'credential__holder').order_by('-created_at')
    
    # Apply search filter if query exists (maintain institution filter)
    if search_query:
        verification_logs = verification_logs.filter(
            Q(credential_id_searched__icontains=search_query) |
            Q(credential__credential_id__icontains=search_query) |
            Q(verifier_email__icontains=search_query) |
            Q(verifier_company__icontains=search_query) |
            Q(credential__holder_name__icontains=search_query) |
            Q(credential__holder__email__icontains=search_query)
        )
    
    # Apply method filter
    if filter_method:
        verification_logs = verification_logs.filter(method=filter_method)
    
    # Apply result filter
    if filter_result:
        verification_logs = verification_logs.filter(result=filter_result)
    
    # Apply date filters
    if filter_date_from:
        verification_logs = verification_logs.filter(created_at__gte=filter_date_from)
    if filter_date_to:
        verification_logs = verification_logs.filter(created_at__lte=filter_date_to)
    
    # Pagination - 20 items per page
    paginator = Paginator(verification_logs, 20)
    page = request.GET.get('page', 1)
    
    try:
        logs_page = paginator.page(page)
    except PageNotAnInteger:
        logs_page = paginator.page(1)
    except EmptyPage:
        logs_page = paginator.page(paginator.num_pages)
    
    # Calculate statistics
    total_logs = verification_logs.count()
    valid_logs = verification_logs.filter(result=VerificationResult.VALID).count()
    invalid_logs = verification_logs.filter(result=VerificationResult.INVALID).count()
    revoked_logs = verification_logs.filter(result=VerificationResult.REVOKED).count()
    
    context = {
        'segment': 'verification-logs',
        'user': request.user,
        'verification_logs': logs_page,
        'search_query': search_query,
        'paginator': paginator,
        'verification_methods': VerificationMethod.choices,
        'verification_results': VerificationResult.choices,
        'institution': institution,
        'filter_method': filter_method,
        'filter_result': filter_result,
        'filter_date_from': filter_date_from,
        'filter_date_to': filter_date_to,
        'total_logs': total_logs,
        'valid_logs': valid_logs,
        'invalid_logs': invalid_logs,
        'revoked_logs': revoked_logs,
    }
    html_template = loader.get_template('institution-admin/verification-logs/index.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def institution_admin_profile(request):
    """Institution Admin - Profile"""
    if request.user.role != 'institution_admin':
        return redirect('dashboard')
    
    from apps.accounts.models import InstitutionAdminProfile
    from apps.institutions.models import Institution
    
    # Get admin profile and institution
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        # If no profile exists, redirect to dashboard
        return redirect('dashboard')
    
    context = {
        'segment': 'inst-profile',
        'user': request.user,
        'admin_profile': admin_profile,
        'institution': institution,
    }
    html_template = loader.get_template('institution-admin/Profile/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@csrf_exempt
def institution_admin_profile_update(request):
    """Update institution admin profile"""
    if request.user.role != 'institution_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    from apps.accounts.models import InstitutionAdminProfile
    import json
    
    try:
        admin_profile = request.user.institution_admin_profile
    except InstitutionAdminProfile.DoesNotExist:
        return JsonResponse({'error': 'Admin profile not found'}, status=404)
    
    if request.method in ['POST', 'PUT', 'PATCH']:
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
            
            # Update user fields
            if 'first_name' in data:
                request.user.first_name = data.get('first_name', '')
            if 'last_name' in data:
                request.user.last_name = data.get('last_name', '')
            if 'phone' in data:
                request.user.phone = data.get('phone', '')
            if 'email' in data:
                # Check if email is already taken by another user
                if User.objects.filter(email=data.get('email')).exclude(id=request.user.id).exists():
                    return JsonResponse({'error': 'Email already exists'}, status=400)
                request.user.email = data.get('email', '')
            
            # Handle avatar upload
            if 'avatar' in request.FILES:
                request.user.avatar = request.FILES['avatar']
            
            request.user.save()
            
            # Update admin profile fields
            if 'department' in data:
                admin_profile.department = data.get('department', '')
            if 'position' in data:
                admin_profile.position = data.get('position', '')
            if 'employee_id' in data:
                admin_profile.employee_id = data.get('employee_id', '')
            
            admin_profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully',
                'user': {
                    'id': str(request.user.id),
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'full_name': request.user.full_name,
                    'phone': request.user.phone,
                    'avatar': request.user.avatar.url if request.user.avatar else None,
                },
                'admin_profile': {
                    'department': admin_profile.department,
                    'position': admin_profile.position,
                    'employee_id': admin_profile.employee_id,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def institution_admin_password_change(request):
    """Change password for institution admin"""
    if request.user.role != 'institution_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        import json
        
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
            
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')
            
            # Validate required fields
            if not old_password:
                return JsonResponse({'error': 'Current password is required'}, status=400)
            if not new_password:
                return JsonResponse({'error': 'New password is required'}, status=400)
            if not confirm_password:
                return JsonResponse({'error': 'Password confirmation is required'}, status=400)
            
            # Check if old password is correct
            if not request.user.check_password(old_password):
                return JsonResponse({'error': 'Current password is incorrect'}, status=400)
            
            # Check if new passwords match
            if new_password != confirm_password:
                return JsonResponse({'error': 'New passwords do not match'}, status=400)
            
            # Check password strength (minimum 8 characters)
            if len(new_password) < 8:
                return JsonResponse({'error': 'Password must be at least 8 characters long'}, status=400)
            
            # Set new password
            request.user.set_password(new_password)
            request.user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Password changed successfully'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
def institution_admin_settings(request):
    """Institution Admin - Settings"""
    if request.user.role != 'institution_admin':
        return redirect('dashboard')
    
    context = {
        'segment': 'inst-settings',  
        'user': request.user,
    }
    html_template = loader.get_template('institution-admin/Settings/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def institution_admin_programs(request):
    """Institution Admin - Programs Management"""
    if request.user.role != 'institution_admin':
        return redirect('dashboard')

    from apps.institutions.models import Program, Institution
    from apps.accounts.models import InstitutionAdminProfile
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.db.models import Q

    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        return redirect('dashboard')

    search_query = request.GET.get('search', '').strip()
    filter_degree_level = request.GET.get('degree_level', '')
    filter_status = request.GET.get('status', '')  # 'active', 'inactive'
    filter_department = request.GET.get('department', '')

    programs = Program.objects.filter(institution=institution).order_by('name')

    if search_query:
        programs = programs.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(faculty__icontains=search_query)
        )
    if filter_degree_level:
        programs = programs.filter(degree_level=filter_degree_level)
    if filter_status:
        programs = programs.filter(is_active=_parse_bool(filter_status))
    if filter_department:
        programs = programs.filter(department__icontains=filter_department)

    paginator = Paginator(programs, 20)
    page = request.GET.get('page', 1)

    try:
        programs_page = paginator.page(page)
    except PageNotAnInteger:
        programs_page = paginator.page(1)
    except EmptyPage:
        programs_page = paginator.page(paginator.num_pages)

    # Get unique departments and degree levels for filters
    departments = Program.objects.filter(institution=institution).exclude(department='').values_list('department', flat=True).distinct().order_by('department')

    context = {
        'segment': 'programs',
        'user': request.user,
        'programs': programs_page,
        'search_query': search_query,
        'paginator': paginator,
        'degree_levels': Program.DegreeLevel.choices,
        'departments': departments,
        'institution': institution,
        'filter_degree_level': filter_degree_level,
        'filter_status': filter_status,
        'filter_department': filter_department,
    }
    html_template = loader.get_template('institution-admin/programs/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@csrf_exempt
def program_create(request):
    """Create a new program"""
    if request.user.role != 'institution_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get institution from admin profile
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        return JsonResponse({'error': 'No institution associated with your account'}, status=400)
    
    if request.method == 'POST':
        from apps.institutions.models import Program
        import json
        
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
            
            # Validate required fields
            if not data.get('name'):
                return JsonResponse({'error': 'Program name is required'}, status=400)
            
            # Check if program code already exists for this institution
            if data.get('code'):
                if Program.objects.filter(institution=institution, code=data.get('code')).exists():
                    return JsonResponse({'error': 'Program code already exists for this institution'}, status=400)
            
            # Create program
            program = Program.objects.create(
                institution=institution,
                name=data.get('name', ''),
                code=data.get('code', ''),
                degree_level=data.get('degree_level', Program.DegreeLevel.BACHELOR),
                department=data.get('department', ''),
                faculty=data.get('faculty', ''),
                duration_years=float(data.get('duration_years')) if data.get('duration_years') else None,
                is_active=_parse_bool(data.get('is_active', True)),
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Program created successfully',
                'program': {
                    'id': str(program.id),
                    'name': program.name,
                    'code': program.code,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def program_update(request, program_id):
    """Update a program"""
    if request.user.role != 'institution_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get institution from admin profile
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        return JsonResponse({'error': 'No institution associated with your account'}, status=400)
    
    from apps.institutions.models import Program
    import uuid
    
    try:
        program = Program.objects.get(id=uuid.UUID(str(program_id)), institution=institution)
    except Program.DoesNotExist:
        return JsonResponse({'error': 'Program not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid program ID'}, status=400)
    
    if request.method in ['POST', 'PUT', 'PATCH']:
        import json
        
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert list values to single values for form data
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
            
            # Validate required fields
            if not data.get('name'):
                return JsonResponse({'error': 'Program name is required'}, status=400)
            
            # Check if program code already exists for this institution (excluding current program)
            if data.get('code'):
                if Program.objects.filter(institution=institution, code=data.get('code')).exclude(id=program.id).exists():
                    return JsonResponse({'error': 'Program code already exists for this institution'}, status=400)
            
            # Update program
            program.name = data.get('name', program.name)
            program.code = data.get('code', program.code)
            program.degree_level = data.get('degree_level', program.degree_level)
            program.department = data.get('department', program.department)
            program.faculty = data.get('faculty', program.faculty)
            program.duration_years = float(data.get('duration_years')) if data.get('duration_years') else program.duration_years
            program.is_active = _parse_bool(data.get('is_active', program.is_active))
            program.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Program updated successfully',
                'program': {
                    'id': str(program.id),
                    'name': program.name,
                    'code': program.code,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def program_delete(request, program_id):
    """Delete a program"""
    if request.user.role != 'institution_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get institution from admin profile
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        return JsonResponse({'error': 'No institution associated with your account'}, status=400)
    
    from apps.institutions.models import Program
    import uuid
    
    try:
        program = Program.objects.get(id=uuid.UUID(str(program_id)), institution=institution)
    except Program.DoesNotExist:
        return JsonResponse({'error': 'Program not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid program ID'}, status=400)
    
    if request.method == 'POST':
        try:
            program_name = program.name
            program.delete()
            return JsonResponse({
                'success': True,
                'message': f'Program "{program_name}" deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url="/login/")
@csrf_exempt
def program_detail(request, program_id):
    """Get program details"""
    if request.user.role != 'institution_admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get institution from admin profile
    try:
        admin_profile = request.user.institution_admin_profile
        institution = admin_profile.institution
    except InstitutionAdminProfile.DoesNotExist:
        return JsonResponse({'error': 'No institution associated with your account'}, status=400)
    
    from apps.institutions.models import Program
    import uuid
    
    try:
        program = Program.objects.get(id=uuid.UUID(str(program_id)), institution=institution)
    except Program.DoesNotExist:
        return JsonResponse({'error': 'Program not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid program ID'}, status=400)
    
    if request.method == 'GET':
        return JsonResponse({
            'id': str(program.id),
            'name': program.name,
            'code': program.code,
            'degree_level': program.degree_level,
            'department': program.department,
            'faculty': program.faculty,
            'duration_years': float(program.duration_years) if program.duration_years else None,
            'is_active': program.is_active,
            'created_at': program.created_at.isoformat() if program.created_at else None,
            'updated_at': program.updated_at.isoformat() if program.updated_at else None,
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ============================================================================
# STUDENT VIEWS
# ============================================================================

@login_required(login_url="/login/")
def student_wallet(request):
    """Student - Credentials Wallet"""
    if request.user.role != 'student':
        return redirect('dashboard')
    
    # Fetch user's credentials
    from apps.credentials.models import Credential
    credentials = Credential.objects.filter(
        holder=request.user
    ).select_related('institution', 'program').order_by('-issue_date', '-created_at')
    
    context = {
        'segment': 'wallet',
        'user': request.user,
        'credentials': credentials,
        'credentials_count': credentials.count(),
    }
    html_template = loader.get_template('student/wallet.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def student_share_qr(request):
    """Student - Share/Download QR"""
    if request.user.role != 'student':
        return redirect('dashboard')
    
    # Fetch student's credentials
    from apps.credentials.models import Credential
    credentials = Credential.objects.filter(holder=request.user).order_by('-issue_date')
    
    context = {
        'segment': 'share-qr',
        'user': request.user,
        'credentials': credentials,
        'credentials_count': credentials.count(),
    }
    html_template = loader.get_template('student/share-qr.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def student_history(request):
    """Student - Verification History"""
    if request.user.role != 'student':
        return redirect('dashboard')
    
    from apps.verifications.models import VerificationLog
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.db.models import Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Get verification logs for student's credentials
    verification_logs = VerificationLog.objects.filter(
        credential__holder=request.user
    ).select_related('credential', 'verifier', 'credential__institution').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        verification_logs = verification_logs.filter(
            Q(credential__credential_id__icontains=search_query) |
            Q(verifier_email__icontains=search_query) |
            Q(verifier_company__icontains=search_query) |
            Q(credential__program_name__icontains=search_query)
        )
    
    # Filter by result
    result_filter = request.GET.get('result', '')
    if result_filter:
        verification_logs = verification_logs.filter(result=result_filter)
    
    # Filter by method
    method_filter = request.GET.get('method', '')
    if method_filter:
        verification_logs = verification_logs.filter(method=method_filter)
    
    # Pagination
    paginator = Paginator(verification_logs, 20)  # Show 20 per page
    page = request.GET.get('page', 1)
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        logs = paginator.page(1)
    except EmptyPage:
        logs = paginator.page(paginator.num_pages)
    
    # Statistics
    total_verifications = verification_logs.count()
    valid_verifications = verification_logs.filter(result='valid').count()
    recent_verifications = verification_logs.filter(
        created_at__gte=now() - timedelta(days=30)
    ).count()
    
    context = {
        'segment': 'student-history',
        'user': request.user,
        'verification_logs': logs,
        'total_verifications': total_verifications,
        'valid_verifications': valid_verifications,
        'recent_verifications': recent_verifications,
        'search_query': search_query,
        'result_filter': result_filter,
        'method_filter': method_filter,
    }
    html_template = loader.get_template('student/history.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def student_profile(request):
    """Student - Profile Settings"""
    if request.user.role != 'student':
        return redirect('dashboard')
    
    from apps.accounts.models import StudentProfile
    
    # Get or create student profile
    student_profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    # Get institution if available
    institution = student_profile.institution if hasattr(student_profile, 'institution') and student_profile.institution else None
    
    context = {
        'segment': 'student-profile',
        'user': request.user,
        'student_profile': student_profile,
        'institution': institution,
    }
    html_template = loader.get_template('student/profile.html')
    return HttpResponse(html_template.render(context, request))


# ============================================================================
# EMPLOYER VIEWS
# ============================================================================

@login_required(login_url="/login/")
def employer_verify_credentials(request):
    """Employer - Verify Credentials"""
    if request.user.role != 'employer':
        return redirect('dashboard')
    
    context = {
        'segment': 'verify-credential',
        'user': request.user,
    }
    html_template = loader.get_template('employer/pages/verify-credentials.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def employer_scan_qr(request):
    """Employer - Scan QR Code"""
    if request.user.role != 'employer':
        return redirect('dashboard')
    
    context = {
        'segment': 'scan-qr',
        'user': request.user,
    }
    html_template = loader.get_template('employer/pages/scan-qr.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def employer_accreditation_lookup(request):
    """Employer - Accreditation Lookup"""
    if request.user.role != 'employer':
        return redirect('dashboard')
    
    from apps.institutions.models import Institution
    from apps.accreditation.models import WHEDRecord, AccreditationLookupLog
    from django.db.models import Q
    
    # Handle AJAX search request
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        import json
        from django.http import JsonResponse
        
        try:
            data = json.loads(request.body)
            search_query = data.get('query', '').strip()
            country_filter = data.get('country', '').strip()
            institution_type_filter = data.get('institution_type', '').strip()
            
            if not search_query:
                return JsonResponse({
                    'success': False,
                    'error': 'Please enter an institution name to search'
                }, status=400)
            
            # Get client IP
            ip_address = request.META.get('REMOTE_ADDR', '')
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            
            # Search institutions in our database
            institution_query = Q(name__icontains=search_query)
            if country_filter:
                institution_query &= Q(country__icontains=country_filter)
            if institution_type_filter:
                institution_query &= Q(institution_type=institution_type_filter)
            
            institutions = Institution.objects.filter(institution_query).select_related()[:20]
            
            # Search WHED records
            whed_query = Q(institution_name__icontains=search_query)
            if country_filter:
                whed_query &= Q(country__icontains=country_filter)
            
            whed_records = WHEDRecord.objects.filter(whed_query)[:20]
            
            # Format results
            institution_results = []
            for inst in institutions:
                institution_results.append({
                    'id': str(inst.id),
                    'name': inst.name,
                    'short_name': inst.short_name,
                    'institution_type': inst.get_institution_type_display(),
                    'country': inst.country,
                    'city': inst.city,
                    'accreditation_status': inst.get_accreditation_status_display(),
                    'accreditation_body': inst.accreditation_body,
                    'accreditation_date': inst.accreditation_date.isoformat() if inst.accreditation_date else None,
                    'accreditation_expiry': inst.accreditation_expiry.isoformat() if inst.accreditation_expiry else None,
                    'is_partner': inst.is_partner,
                    'is_verified': inst.is_verified,
                    'website': inst.website,
                    'email': inst.email,
                    'phone': inst.phone,
                    'founded_year': inst.founded_year,
                    'source': 'certchain'
                })
            
            whed_results = []
            for whed in whed_records:
                whed_results.append({
                    'id': str(whed.id),
                    'whed_id': whed.whed_id,
                    'name': whed.institution_name,
                    'name_local': whed.institution_name_local,
                    'country': whed.country,
                    'city': whed.city,
                    'institution_type': whed.institution_type,
                    'is_accredited': whed.is_accredited,
                    'accreditation_body': whed.accreditation_body,
                    'website': whed.website,
                    'email': whed.email,
                    'phone': whed.phone,
                    'founded_year': whed.founded_year,
                    'linked_institution_id': str(whed.linked_institution.id) if whed.linked_institution else None,
                    'source': 'whed'
                })
            
            # Log the lookup
            try:
                AccreditationLookupLog.objects.create(
                    search_query=search_query,
                    search_type='institution_name',
                    results_count=len(institution_results) + len(whed_results),
                    user=request.user,
                    ip_address=ip_address
                )
            except:
                pass
            
            return JsonResponse({
                'success': True,
                'institutions': institution_results,
                'whed_records': whed_results,
                'total_results': len(institution_results) + len(whed_results)
            })
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in accreditation lookup: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }, status=500)
    
    # Get unique countries and institution types for filters
    from apps.institutions.models import InstitutionType
    countries = Institution.objects.values_list('country', flat=True).distinct().order_by('country')
    institution_types = InstitutionType.choices
    
    context = {
        'segment': 'employer-accreditation',
        'user': request.user,
        'countries': countries,
        'institution_types': institution_types,
    }
    html_template = loader.get_template('employer/pages/accreditation-lookup.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def employer_history(request):
    """Employer - Verification History"""
    if request.user.role != 'employer':
        return redirect('dashboard')
    
    from apps.verifications.models import VerificationLog, VerificationResult
    from django.db.models import Q, Count
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Get all verification logs for this employer
    verification_logs = VerificationLog.objects.filter(
        verifier=request.user
    ).select_related('credential', 'credential__institution', 'credential__holder').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        verification_logs = verification_logs.filter(
            Q(credential_id_searched__icontains=search_query) |
            Q(credential__credential_id__icontains=search_query) |
            Q(credential__holder_name__icontains=search_query) |
            Q(credential__institution__name__icontains=search_query)
        )
    
    # Filter by result
    result_filter = request.GET.get('result', '')
    if result_filter:
        verification_logs = verification_logs.filter(result=result_filter)
    
    # Filter by method
    method_filter = request.GET.get('method', '')
    if method_filter:
        verification_logs = verification_logs.filter(method=method_filter)
    
    # Filter by date range
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            verification_logs = verification_logs.filter(created_at__date__gte=date_from_obj)
        except:
            pass
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            verification_logs = verification_logs.filter(created_at__date__lte=date_to_obj)
        except:
            pass
    
    # Calculate statistics
    total_verifications = VerificationLog.objects.filter(verifier=request.user).count()
    valid_verifications = VerificationLog.objects.filter(verifier=request.user, result=VerificationResult.VALID).count()
    recent_verifications = VerificationLog.objects.filter(
        verifier=request.user,
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Pagination
    paginator = Paginator(verification_logs, 20)  # Show 20 per page
    page = request.GET.get('page', 1)
    try:
        logs_page = paginator.page(page)
    except PageNotAnInteger:
        logs_page = paginator.page(1)
    except EmptyPage:
        logs_page = paginator.page(paginator.num_pages)
    
    context = {
        'segment': 'employer-history',
        'user': request.user,
        'verification_logs': logs_page,
        'total_verifications': total_verifications,
        'valid_verifications': valid_verifications,
        'recent_verifications': recent_verifications,
        'search_query': search_query,
        'result_filter': result_filter,
        'method_filter': method_filter,
        'date_from': date_from,
        'date_to': date_to,
        'result_choices': VerificationResult.choices,
        'method_choices': [
            ('credential_id', 'Credential ID'),
            ('blockchain_hash', 'Blockchain Hash'),
            ('qr_code', 'QR Code'),
            ('share_link', 'Share Link'),
            ('api', 'API'),
        ],
    }
    html_template = loader.get_template('employer/pages/history.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def employer_profile(request):
    """Employer - Profile"""
    if request.user.role != 'employer':
        return redirect('dashboard')
    
    context = {
        'segment': 'employer-profile',
        'user': request.user,
    }
    html_template = loader.get_template('employer/pages/profile.html')
    return HttpResponse(html_template.render(context, request))



def ajax_data_color_general(request):
    new_color = request.GET.get('new_color')
    user = User.objects.get(pk=request.user.id)
    user.data_color_general = new_color
    user.save()
    return HttpResponse("")

def ajax_sidebar_data_background_color(request):
    new_color = request.GET.get('new_color')
    user = User.objects.get(pk=request.user.id)
    user.data_background_color = new_color
    user.save()
    return HttpResponse("")

def ajax_data_image(request):
    new_image = request.GET.get('new_image')
    user = User.objects.get(pk=request.user.id)
    user.data_image = new_image
    user.save()
    return HttpResponse("")

def ajax_volume_onof(request):
    onof = request.POST['onof']
    user = User.objects.get(pk=request.user.id)
    if onof =="ON":
        user.chat_volume = False
    else:
        user.chat_volume = True
    user.save()
    return HttpResponse("DATA")





@login_required(login_url="/login/")
def pages(request):

    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template

        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))
    except PermissionDenied:

        html_template = loader.get_template( 'accounts/login.html' )
        return HttpResponse(html_template.render(context, request))
    except:
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))




def ban_User(request, id):    
    user = User.objects.get(pk=id)
    if (user.is_Ban):
        user.is_Ban =False
    else:
        user.is_Ban =True
        
    user.save() 
    return JsonResponse({'ban': True})

def Unban_User(request, id):    
    user = User.objects.get(pk=id)
    user.is_active = True
    user.is_Ban =False
    user.save() 
    return JsonResponse({'ban': True})





def about_us(request):
    """Public About page with dynamic team and stats"""
    # If later you add a Content model for About, wire it here
    objects = None

    settings = GeneralSettings.objects.all().first()


    context = {
        'segment': 'about',
        'objects': objects,
        'settings': settings,
    }

    html_template = loader.get_template('about.html')
    return HttpResponse(html_template.render(context, request))

def fuzzy_search(model, field_name, link_field, desc_field, query, threshold=80, limit=5):
    if not query:
        return []

    # Get all items from the model
    items = model.objects.all()

    # Perform fuzzy matching on the specified field values
    matched_items = process.extract(query, [getattr(item, field_name) for item in items], scorer=fuzz.WRatio, limit=limit)

    # Only include the items that have a high enough fuzzy match score (above threshold)
    result_items = []
    for match in matched_items:
        score = match[1]
        if score >= threshold:
            item_value = match[0]
            matching_items = model.objects.filter(**{field_name: item_value})
            result_items.extend(matching_items)

    return result_items




def contact_us(request):  
    context = {}
    msg = None
    msg2 = None
    settings = GeneralSettings.objects.all().first()

    if request.method == "POST":
        form2 = ContactForm(request.POST)

        if form2.is_valid():
            email = form2.cleaned_data.get("email")
            name = form2.cleaned_data.get("name")
            phone = form2.cleaned_data.get("phone", '')
            email_subject = form2.cleaned_data.get("subject")
            interest = form2.cleaned_data.get("interest", '')
            message = form2.cleaned_data.get("message")
            
            # Save to database
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone if phone else None,
                subject=email_subject,
                interest=interest if interest else None,
                message=message,
                status='new'
            )
            
            context = {
                    'message': message,
                    'email': email,
                    'phone': phone,
                    'interest': interest,
					'email_subject': email_subject ,
                    'name': name,
                }
            subject, from_email, to_email = email_subject,setting.DEFAULT_FROM_EMAIL, email
            template = get_template('accounts/emails/feedback.html', using='post_office')
            html = template.render(context)
            email_message = EmailMultiAlternatives(subject, html, from_email, [to_email])
            email_message.content_subtype = 'html'
            template.attach_related(email_message)
            email_message.send()  
            
            
            email2 ="promewsl@gmail.com"
            
            subject, from_email, to_email = email_subject,setting.DEFAULT_FROM_EMAIL, email2
            template = get_template('accounts/emails/contactUs.html', using='post_office')
            html = template.render(context)
            email_message = EmailMultiAlternatives(subject, html, from_email, [to_email])
            email_message.content_subtype = 'html'
            template.attach_related(email_message)
            email_message.send()  
            
            msg2 = 'Message Successfully  Sent'   
        else:
            msg2 = 'Error validating the form'
           
            

    form2 = ContactForm()         
    #print (settings)

    settings = GeneralSettings.objects.all().first()
    context = {
        'segment': 'contact',
        'form2' : form2,
        'msg' : msg,
        'msg2' : msg2,
        'settings' : settings,
            }
    

    html_template = loader.get_template( 'contact.html' )
    return HttpResponse(html_template.render(context, request))




@login_required(login_url="/login/")
def update_GeneralSettings(request):
    context = {}
    contentType = 'Update "General Settings" '
    settings = GeneralSettings.objects.all().first()
    if request.method == "POST":
        context['segment'] = 'update_GeneralSettings'   
        my_record = GeneralSettings.objects.all().first()
        form = GeneralSettingsForm (request.POST, request.FILES, instance=my_record)
        if form.is_valid():
            form.save()
            sweetify.success(request, 'You did it', text='Good job!  updated General Settings Contents ', persistent='Ok')
            return redirect("update_GeneralSettings") 
   
    
    else:  
        my_record = GeneralSettings.objects.all().first()
        form = GeneralSettingsForm(instance=my_record)
        context = {
			'segment': 'update_GeneralSettings',
            'contentType' :contentType,
			'form' : form, 
            'settings' : settings,
		}
     
    html_template = loader.get_template( 'core/settings/form2.html' )
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def contact_messages_list(request):
    """List all contact messages (admin view)"""
    messages = ContactMessage.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        messages = messages.filter(status=status_filter)
    
    # Count by status
    new_count = ContactMessage.objects.filter(status='new').count()
    read_count = ContactMessage.objects.filter(status='read').count()
    replied_count = ContactMessage.objects.filter(status='replied').count()
    archived_count = ContactMessage.objects.filter(status='archived').count()
    
    context = {
        'segment': 'contact_messages',
        'messages': messages,
        'new_count': new_count,
        'read_count': read_count,
        'replied_count': replied_count,
        'archived_count': archived_count,
        'status_filter': status_filter,
    }
    
    html_template = loader.get_template('contact/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def contact_message_detail(request, pk):
    """View detailed contact message (admin view)"""
    message = get_object_or_404(ContactMessage, pk=pk)
    
    # Mark as read when viewing
    if message.status == 'new':
        message.mark_as_read(request.user)
    
    context = {
        'segment': 'contact_messages',
        'message': message,
    }
    
    html_template = loader.get_template('contact/detail.html')
    return HttpResponse(html_template.render(context, request))


@csrf_exempt
@login_required(login_url="/login/")
def update_contact_status(request, pk):
    """Update status of a contact message"""
    if request.method == 'POST':
        try:
            message = get_object_or_404(ContactMessage, pk=pk)
            status = request.POST.get('status')
            notes = request.POST.get('notes', '')
            
            if status in dict(ContactMessage.STATUS_CHOICES):
                message.status = status
                if notes:
                    message.notes = notes
                
                # Handle replied status
                if status == 'replied':
                    message.mark_as_replied(request.user)
                else:
                    message.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Status updated to {message.get_status_display()} successfully!'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid status value'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
@login_required(login_url="/login/")
def delete_contact_message(request, pk):
    """Delete a contact message"""
    if request.method == 'DELETE' or request.method == 'POST':
        try:
            message = get_object_or_404(ContactMessage, pk=pk)
            message.delete()
            return JsonResponse({'status': 'success', 'message': 'Message deleted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
@login_required(login_url="/login/")
def send_contact_reply(request, pk):
    """Send email reply to contact message"""
    if request.method == 'POST':
        try:
            message = get_object_or_404(ContactMessage, pk=pk)
            subject = request.POST.get('subject', '')
            reply_body = request.POST.get('message', '')
            
            # Debug logging
            import logging
            logger = logging.getLogger(__name__)
            print(f"Processing email reply for message {pk}: subject='{subject}', reply_body length={len(reply_body)}")
            
            if not subject or not reply_body:
                logger.warning(f"Missing required fields: subject='{subject}', reply_body length={len(reply_body)}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Subject and message are required'
                }, status=400)
            
            # Prepare context for email template
            context = {
                'original_message': message,
                'reply_message': reply_body,
                'request': request,
            }
            
            # Send email using template
            try:
                from django.template.loader import get_template
                from django.core.mail import EmailMultiAlternatives
                import logging
                
                logger = logging.getLogger(__name__)
                
                # Render the email template
                try:
                    template = get_template('accounts/emails/contact_reply.html')
                    html_content = template.render(context)
                    print("Email template rendered successfully")
                except Exception as template_error:
                    print(f"Template rendering failed: {str(template_error)}")
                    # Fallback to simple text email
                    html_content = f"""
                    <html>
                    <body>
                        <h2>Reply from Apple of God</h2>
                        <p>Dear {message.name},</p>
                        <p>{reply_body}</p>
                        <p>Best regards,<br>Apple of God Team</p>
                    </body>
                    </html>
                    """
                
                # Create email message
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=reply_body,  # Plain text fallback
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[message.email],
                    reply_to=[settings.DEFAULT_FROM_EMAIL],
                )
                
                # Attach HTML content
                email.attach_alternative(html_content, "text/html")
                
                # Send with timeout to prevent hanging
                import socket
                default_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(10)  # 10 second timeout
                try:
                    email.send(fail_silently=False)
                    print(f"Email sent successfully to {message.email}")
                finally:
                    socket.setdefaulttimeout(default_timeout)
                
                # Mark as replied
                message.mark_as_replied(request.user)
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Reply sent successfully to {message.email}'
                })
            except Exception as email_error:
                # Log the error but don't mark as replied
                import logging
                logger = logging.getLogger(__name__)
                print(f"Failed to send email: {str(email_error)}")
                
                return JsonResponse({
                    'status': 'error',
                    'message': f'Failed to send email: {str(email_error)}'
                }, status=500)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to send email: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
@login_required(login_url="/login/")
def test_email_system(request):
    """Test email system - for debugging purposes"""
    if request.method == 'POST':
        try:
            from django.template.loader import get_template
            from django.core.mail import EmailMultiAlternatives
            import logging
            from django.utils import timezone
            
            logger = logging.getLogger(__name__)
            
            # Test email template rendering
            context = {
                'original_message': {
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'subject': 'Test Subject',
                    'message': 'Test message content',
                    'created_at': timezone.now()
                },
                'reply_message': 'This is a test reply message.',
                'request': request,
            }
            
            try:
                template = get_template('accounts/emails/contact_reply.html')
                html_content = template.render(context)
                print("Test email template rendered successfully")
            except Exception as template_error:
                print(f"Test template rendering failed: {str(template_error)}")
                return JsonResponse({
                    'status': 'error',
                    'message': f'Template rendering failed: {str(template_error)}'
                }, status=500)
            
            # Test email sending
            email = EmailMultiAlternatives(
                subject='Test Email from Apple of God',
                body='This is a test email.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['test@example.com'],
            )
            
            email.attach_alternative(html_content, "text/html")
            
            # Send with timeout
            import socket
            default_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(10)
            try:
                email.send(fail_silently=False)
                print("Test email sent successfully")
            finally:
                socket.setdefaulttimeout(default_timeout)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Test email sent successfully'
            })
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            print(f"Test email failed: {str(e)}")
            
            return JsonResponse({
                'status': 'error',
                'message': f'Test email failed: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required(login_url="/login/")
def test_email_page(request):
    """Test email page for debugging"""
    return render(request, 'test_email.html')



@login_required(login_url="/login/")
def visitor_analytics(request):
    """Display visitor analytics per month"""
    from apps.home.models import Visitor
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import datetime, timedelta
    from calendar import month_name
    
    # Get selected month and year from query params (default to current month)
    selected_month = request.GET.get('month', timezone.now().month)
    selected_year = request.GET.get('year', timezone.now().year)
    
    try:
        selected_month = int(selected_month)
        selected_year = int(selected_year)
    except (ValueError, TypeError):
        selected_month = timezone.now().month
        selected_year = timezone.now().year
    
    # Get all visitors for the selected month
    visitors = Visitor.objects.filter(
        visited_at__year=selected_year,
        visited_at__month=selected_month
    )
    
    # Total visits
    total_visits = visitors.count()
    
    # Unique visitors (by IP address)
    unique_visitors = visitors.values('ip_address').distinct().count()
    
    # Unique sessions
    unique_sessions = visitors.exclude(session_key__isnull=True).values('session_key').distinct().count()
    
    # Visits per day in the month
    from django.db.models.functions import TruncDate
    daily_visits = visitors.annotate(
        day=TruncDate('visited_at')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Top pages
    top_pages = visitors.values('path').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Browser statistics
    browser_stats = visitors.exclude(browser__isnull=True).values('browser').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # OS statistics
    os_stats = visitors.exclude(os__isnull=True).values('os').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Device type statistics
    device_stats = visitors.exclude(device_type__isnull=True).values('device_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Referrer statistics
    referrer_stats = visitors.exclude(referer__isnull=True).exclude(referer='').values('referer').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Get previous and next month/year for navigation
    if selected_month == 1:
        prev_month = 12
        prev_year = selected_year - 1
    else:
        prev_month = selected_month - 1
        prev_year = selected_year
    
    if selected_month == 12:
        next_month = 1
        next_year = selected_year + 1
    else:
        next_month = selected_month + 1
        next_year = selected_year
    
    # Get available years (years that have visitor data)
    available_years = Visitor.objects.dates('visited_at', 'year').values_list('visited_at__year', flat=True).distinct()
    
    # Recent visitors (last 20)
    recent_visitors = visitors.order_by('-visited_at')[:20]
    
    context = {
        'segment': 'analytics',
        'total_visits': total_visits,
        'unique_visitors': unique_visitors,
        'unique_sessions': unique_sessions,
        'daily_visits': daily_visits,
        'top_pages': top_pages,
        'browser_stats': browser_stats,
        'os_stats': os_stats,
        'device_stats': device_stats,
        'referrer_stats': referrer_stats,
        'recent_visitors': recent_visitors,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_name': month_name[selected_month],
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'available_years': available_years,
    }
    
    html_template = loader.get_template('analytics/visitors.html')
    return HttpResponse(html_template.render(context, request))

@csrf_exempt
def public_accreditation_search(request):
    """Public API endpoint for accreditation search (used on home page)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        search_query = data.get('institution_name', '').strip()
        country = data.get('country', '').strip()
        institution_type = data.get('institution_type', '').strip()
        
        from apps.institutions.models import Institution
        from django.db.models import Q
        
        # Search in CertChain database
        institutions = Institution.objects.filter(is_active=True)
        
        if search_query:
            institutions = institutions.filter(
                Q(name__icontains=search_query) |
                Q(short_name__icontains=search_query)
            )
        
        if country:
            institutions = institutions.filter(country=country)
        
        if institution_type:
            institutions = institutions.filter(institution_type=institution_type)
        
        # Limit results
        institutions = institutions[:20]
        
        # Format results
        institution_results = []
        for inst in institutions:
            institution_results.append({
                'id': str(inst.id),
                'name': inst.name,
                'short_name': inst.short_name,
                'country': inst.country or '',
                'city': inst.city or '',
                'institution_type': inst.get_institution_type_display() if inst.institution_type else '',
                'accreditation_status': inst.accreditation_status or 'Not Specified',
                'is_partner': inst.is_partner,
                'is_verified': inst.is_verified,
                'source': 'CertChain'
            })
        
        # For WHED records, you would integrate with WHED API here
        # For now, return empty list
        whed_results = []
        
        return JsonResponse({
            'success': True,
            'institutions': institution_results,
            'whed_records': whed_results,
            'total_results': len(institution_results) + len(whed_results)
        })
          
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in public accreditation search: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)


@csrf_exempt
def public_live_activities(request):
    """Public API endpoint for live verification activities (used on home page)"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        from apps.verifications.models import VerificationLog, VerificationResult
        from django.utils import timezone
        from datetime import timedelta
        from django.utils.timesince import timesince
        
        # Get recent verification logs (last 24 hours, limit to 10)
        recent_logs = VerificationLog.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24),
            result=VerificationResult.VALID
        ).select_related('credential', 'credential__institution', 'verifier').order_by('-created_at')[:10]
        
        activities = []
        for log in recent_logs:
            # Determine activity type
            activity_type = "success"
            if log.result == VerificationResult.REVOKED:
                activity_type = "error"
            elif log.result == VerificationResult.NOT_FOUND:
                activity_type = "warning"
            
            # Build activity text
            if log.credential:
                institution_name = log.credential.institution.name if log.credential.institution else "Unknown Institution"
                verifier_name = log.verifier_company or log.verifier_email or "An employer"
                activity_text = f"<strong>{verifier_name}</strong> verified credential from {institution_name}"
            elif log.verifier_company:
                activity_text = f"<strong>{log.verifier_company}</strong> verified a credential"
            else:
                activity_text = "A credential was verified"
            
            # Calculate time ago
            time_ago = timesince(log.created_at)
            if "minute" in time_ago.lower():
                time_ago = time_ago.split(",")[0] + " ago"
            elif "hour" in time_ago.lower():
                time_ago = time_ago.split(",")[0] + " ago"
            else:
                time_ago = "Recently"
            
            activities.append({
                'type': activity_type,
                'text': activity_text,
                'time': time_ago
            })
        
        # If no recent activities, return some default messages
        if not activities:
            activities = [
                {
                    'type': 'success',
                    'text': 'System is ready for verifications',
                    'time': 'Just now'
                }
            ]
        
        return JsonResponse({
            'success': True,
            'activities': activities
        })
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in public live activities: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}',
            'activities': []
        }, status=500)


@csrf_exempt
def public_institutions_list(request):
    """Public API endpoint for institutions list (used for autocomplete and display)"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        from apps.institutions.models import Institution
        from apps.accreditation.models import WHEDRecord
        from django.db.models import Q
        
        # Get all active institutions
        institutions = Institution.objects.filter(is_active=True).order_by('name')
        
        # Format institutions
        institution_list = []
        for inst in institutions:
            institution_list.append({
                'name': inst.name,
                'short_name': inst.short_name or '',
                'country': inst.country or '',
                'countryCode': inst.country or '',
                'city': inst.city or '',
                'accredited': inst.accreditation_status and 'accredited' in inst.accreditation_status.lower(),
                'whedId': inst.whed_id or '',
                'founded': inst.founded_year if hasattr(inst, 'founded_year') else None,
                'type': inst.get_institution_type_display() if inst.institution_type else '',
                'recognition': inst.accreditation_status or '',
                'website': inst.website or '',
                'verificationContact': inst.email or '',
                'partnerStatus': inst.is_partner,
                'is_partner': inst.is_partner,
                'degrees': ['Bachelor\'s', 'Master\'s', 'Doctorate'] if inst.is_partner else [],
                'studentCount': 0,  # Can be added if available in model
                'programs': [],  # Can be populated from Program model if available
                'accreditationHistory': []
            })
        
        # Get WHED records (if available)
        whed_records = []
        try:
            whed_institutions = WHEDRecord.objects.all()[:50]  # Limit to 50
            for whed in whed_institutions:
                whed_records.append({
                    'name': whed.institution_name,
                    'country': whed.country or '',
                    'countryCode': whed.country or '',
                    'city': whed.city or '',
                    'whedId': whed.whed_id or '',
                    'accredited': True,
                    'partnerStatus': False,
                    'is_partner': False
                })
        except:
            pass  # If WHEDRecord doesn't exist, skip
        
        return JsonResponse({
            'success': True,
            'institutions': institution_list,
            'whed_records': whed_records,
            'total': len(institution_list) + len(whed_records)
        })
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in public institutions list: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}',
            'institutions': [],
            'whed_records': []
        }, status=500)


@csrf_exempt
def public_credential_search(request):
    """Public API endpoint for searching credentials by name, institution, and year"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        holder_name = data.get('holder_name', '').strip()
        institution = data.get('institution', '').strip()
        year = data.get('year', '').strip()
        
        from apps.credentials.models import Credential, CredentialStatus
        from apps.institutions.models import Institution
        from django.db.models import Q
        from django.utils import timezone
        from datetime import datetime
        
        # Start with all issued credentials (public search only shows issued credentials)
        credentials = Credential.objects.filter(
            status=CredentialStatus.ISSUED
        ).select_related('holder', 'institution').order_by('-issue_date')
        
        # Apply filters
        if holder_name:
            credentials = credentials.filter(
                Q(holder_name__icontains=holder_name) |
                Q(holder__first_name__icontains=holder_name) |
                Q(holder__last_name__icontains=holder_name)
            )
        
        if institution:
            # Map institution short names to actual institution names
            institution_map = {
                'usl': 'University of Sierra Leone',
                'njala': 'Njala University',
                'limkokwing': 'Limkokwing University',
                'limkokwing-university': 'Limkokwing University',
                'ipam': 'IPAM',
                'bluecrest': 'BlueCrest College',
                'bluecrest-college': 'BlueCrest College'
            }
            
            # Check if it's a mapped short name or actual name
            institution_name = institution_map.get(institution.lower(), institution)
            
            # Also try to match by converting dashes to spaces
            if institution_name == institution:
                institution_name = institution.replace('-', ' ')
            
            if institution_name.lower() == 'other' or institution.lower() == 'other':
                # For "other", don't filter by institution
                pass
            else:
                # Try exact match first, then partial match
                credentials = credentials.filter(
                    Q(institution__name__icontains=institution_name) |
                    Q(institution__short_name__icontains=institution_name) |
                    Q(institution__name__iexact=institution_name)
                )
        
        if year:
            try:
                year_int = int(year)
                # Filter by completion_date or issue_date year
                credentials = credentials.filter(
                    Q(completion_date__year=year_int) |
                    Q(issue_date__year=year_int)
                )
            except ValueError:
                pass  # Invalid year, ignore
        
        # Limit results to 20
        credentials = credentials[:20]
        
        # Format results
        credential_results = []
        for cred in credentials:
            credential_results.append({
                'credential_id': cred.credential_id,
                'holder_name': cred.holder_name,
                'institution': cred.institution.name if cred.institution else '',
                'program_name': cred.program_name,
                'degree_level': cred.degree_level,
                'completion_date': cred.completion_date.isoformat() if cred.completion_date else None,
                'issue_date': cred.issue_date.isoformat() if cred.issue_date else None,
                'grade': cred.grade,
                'status': cred.status
            })
        
        return JsonResponse({
            'success': True,
            'credentials': credential_results,
            'total_results': len(credential_results)
        })
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in public credential search: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}',
            'credentials': [],
            'total_results': 0
        }, status=500)
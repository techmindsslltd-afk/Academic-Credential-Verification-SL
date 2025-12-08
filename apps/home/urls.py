# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present TechMinds SL Ltd
"""

from django.urls import path, re_path
from apps.home import views
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static
from django.conf import settings

from django.views.i18n import set_language

from .views import * 


urlpatterns = [

    path('', views.index, name='home'),

    path('set_language/', set_language, name='set_language'),
    path('set_languagemain/', views.set_language, name='set_languagemian'),
    path('dashboard', views.dashboard, name='dashboard'),
   
 
    path('volume_onof', csrf_exempt(
        views.ajax_volume_onof), name="volume_onof"),
    
    path('ajax_data_color_general', csrf_exempt(views.ajax_data_color_general), name="ajax_data_color_general"),
    path('ajax_sidebar_data_background_color', csrf_exempt(views.ajax_sidebar_data_background_color), name="ajax_sidebar_data_background_color"),
    path('ajax_data_image', csrf_exempt(views.ajax_data_image), name="ajax_data_image"),
    
    path('ban_user/<int:id>',
         csrf_exempt(views.ban_User), name="ban_user"),
   
    path('Unban_user/<int:id>',
         csrf_exempt(views.Unban_User), name="Unban_user"),

    path('about', views.about_us, name='about'),
    path('contact/', views.contact_us, name='contact'),

    path('update_GeneralSettings', views.update_GeneralSettings, name='update_GeneralSettings'),  

    # ============= Contact Message Management URLs =============
    
    path('admin/contact-messages/', views.contact_messages_list, name='contact_messages_list'),
    path('admin/contact-messages/<int:pk>/', views.contact_message_detail, name='contact_message_detail'),
    path('admin/contact-messages/<int:pk>/update-status/', csrf_exempt(views.update_contact_status), name='update_contact_status'),
    path('admin/contact-messages/<int:pk>/delete/', csrf_exempt(views.delete_contact_message), name='delete_contact_message'),
    path('admin/contact-messages/<int:pk>/send-reply/', csrf_exempt(views.send_contact_reply), name='send_contact_reply'),
    path('admin/test-email/', csrf_exempt(views.test_email_system), name='test_email_system'),
    path('admin/test-email-page/', views.test_email_page, name='test_email_page'),

    # ============================================================================
    # SUPER ADMIN URLs
    # ============================================================================
    path('super-admin/dashboard/', views.super_admin_dashboard, name='super_admin_dashboard'),
    path('super-admin/institutions/', views.super_admin_institutions, name='super_admin_institutions'),
    path('super-admin/institutions/create/', views.institution_create, name='institution_create'),
    path('super-admin/institutions/<uuid:institution_id>/', views.institution_detail, name='institution_detail'),
    path('super-admin/institutions/<uuid:institution_id>/update/', views.institution_update, name='institution_update'),
    path('super-admin/institutions/<uuid:institution_id>/delete/', views.institution_delete, name='institution_delete'),
    path('super-admin/users/', views.super_admin_users, name='super_admin_users'),
    path('super-admin/users/create/', views.user_create, name='user_create'),
    path('super-admin/users/<uuid:user_id>/', views.user_detail, name='user_detail'),
    path('super-admin/users/<uuid:user_id>/update/', views.user_update, name='user_update'),
    path('super-admin/users/<uuid:user_id>/delete/', views.user_delete, name='user_delete'),
    path('super-admin/accreditation/', views.super_admin_accreditation, name='super_admin_accreditation'),
    path('super-admin/accreditation/create/', views.accreditation_record_create, name='accreditation_record_create'),
    path('super-admin/accreditation/<uuid:record_id>/', views.accreditation_record_detail, name='accreditation_record_detail'),
    path('super-admin/accreditation/<uuid:record_id>/update/', views.accreditation_record_update, name='accreditation_record_update'),
    path('super-admin/accreditation/<uuid:record_id>/delete/', views.accreditation_record_delete, name='accreditation_record_delete'),
    path('super-admin/ledger/', views.super_admin_ledger, name='super_admin_ledger'),
    path('super-admin/analytics/', views.super_admin_analytics, name='super_admin_analytics'),
    path('super-admin/settings/', views.super_admin_settings, name='super_admin_settings'),

    # ============================================================================
    # INSTITUTION ADMIN URLs
    # ============================================================================
    path('institution-admin/dashboard/', views.institution_admin_dashboard, name='institution_admin_dashboard'),
    path('institution-admin/issue-credentials/', views.institution_admin_issue_credentials, name='institution_admin_issue_credentials'),
    path('institution-admin/credentials/create/', views.credential_create, name='credential_create'),
    path('institution-admin/credentials/<uuid:credential_id>/', views.credential_detail, name='credential_detail'),
    path('institution-admin/credentials/<uuid:credential_id>/update/', views.credential_update, name='credential_update'),
    path('institution-admin/credentials/<uuid:credential_id>/delete/', views.credential_delete, name='credential_delete'),
    path('institution-admin/students/', views.institution_admin_students, name='institution_admin_students'),
    path('institution-admin/students/create/', views.student_create, name='student_create'),
    path('institution-admin/students/<uuid:student_id>/', views.student_detail, name='student_detail'),
    path('institution-admin/students/<uuid:student_id>/update/', views.student_update, name='student_update'),
    path('institution-admin/students/<uuid:student_id>/delete/', views.student_delete, name='student_delete'),
    path('institution-admin/programs/', views.institution_admin_programs, name='institution_admin_programs'),
    path('institution-admin/programs/create/', views.program_create, name='program_create'),
    path('institution-admin/programs/<uuid:program_id>/', views.program_detail, name='program_detail'),
    path('institution-admin/programs/<uuid:program_id>/update/', views.program_update, name='program_update'),
    path('institution-admin/programs/<uuid:program_id>/delete/', views.program_delete, name='program_delete'),
    path('institution-admin/verification-logs/', views.institution_admin_verification_logs, name='institution_admin_verification_logs'),
    path('institution-admin/profile/', views.institution_admin_profile, name='institution_admin_profile'),
    path('institution-admin/profile/update/', views.institution_admin_profile_update, name='institution_admin_profile_update'),
    path('institution-admin/profile/change-password/', views.institution_admin_password_change, name='institution_admin_password_change'),
    path('institution-admin/settings/', views.institution_admin_settings, name='institution_admin_settings'),

    # ============================================================================
    # STUDENT URLs
    # ============================================================================
    path('student/wallet/', views.student_wallet, name='student_wallet'),
    path('student/share-qr/', views.student_share_qr, name='student_share_qr'),
    path('student/history/', views.student_history, name='student_history'),
    path('student/profile/', views.student_profile, name='student_profile'),
  
    # ============================================================================
    # EMPLOYER URLs
    # ============================================================================
    path('employer/verify-credentials/', views.employer_verify_credentials, name='employer_verify_credentials'),
    path('employer/scan-qr/', views.employer_scan_qr, name='employer_scan_qr'),
    path('employer/accreditation-lookup/', views.employer_accreditation_lookup, name='employer_accreditation_lookup'),
    path('employer/history/', views.employer_history, name='employer_history'),
    path('employer/profile/', views.employer_profile, name='employer_profile'),
    
    # Public accreditation search endpoint (for home page)
    path('api/public/accreditation/search/', views.public_accreditation_search, name='public_accreditation_search'),
    
    # Public API endpoints for home page dynamic data
    path('api/public/live-activities/', csrf_exempt(views.public_live_activities), name='public_live_activities'),
    path('api/public/institutions/list/', csrf_exempt(views.public_institutions_list), name='public_institutions_list'),
    path('api/public/credentials/search/', csrf_exempt(views.public_credential_search), name='public_credential_search'),

] 
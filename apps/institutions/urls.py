"""
URL configuration for institutions app
"""
from django.urls import path
from .views import (
    InstitutionListView, InstitutionDetailView, InstitutionCreateView,
    InstitutionUpdateView, InstitutionDeleteView, ProgramListView,
    ProgramDetailView, AccreditationRecordListView, whed_lookup,
    BulkUploadInstitutionsView
)

urlpatterns = [
    path('', InstitutionListView.as_view(), name='institution_list'),
    path('create/', InstitutionCreateView.as_view(), name='institution_create'),
    path('<uuid:id>/', InstitutionDetailView.as_view(), name='institution_detail'),
    path('<uuid:id>/update/', InstitutionUpdateView.as_view(), name='institution_update'),
    path('<uuid:id>/delete/', InstitutionDeleteView.as_view(), name='institution_delete'),
    
    # Programs
    path('programs/', ProgramListView.as_view(), name='program_list'),
    path('programs/<uuid:id>/', ProgramDetailView.as_view(), name='program_detail'),
    
    # Accreditation
    path('accreditation-records/', AccreditationRecordListView.as_view(), name='accreditation_list'),
    
    # WHED lookup
    path('whed-lookup/', whed_lookup, name='whed_lookup'),
    
    # Bulk upload
    path('bulk-upload/', BulkUploadInstitutionsView.as_view(), name='institution_bulk_upload'),
]

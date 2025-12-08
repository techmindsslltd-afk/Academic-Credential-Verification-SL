"""
URL configuration for accreditation app
"""
from django.urls import path
from .views import (
    AccreditationBodyListView, AccreditationBodyDetailView,
    WHEDSearchView, WHEDRecordDetailView,
    AccreditationLookupLogListView, country_list
)

urlpatterns = [
    # Accreditation bodies
    path('bodies/', AccreditationBodyListView.as_view(), name='accreditation_body_list'),
    path('bodies/<uuid:id>/', AccreditationBodyDetailView.as_view(), name='accreditation_body_detail'),
    
    # WHED search
    path('whed/search/', WHEDSearchView.as_view(), name='whed_search'),
    path('whed/<str:whed_id>/', WHEDRecordDetailView.as_view(), name='whed_detail'),
    
    # Lookup logs
    path('lookup-logs/', AccreditationLookupLogListView.as_view(), name='lookup_logs'),
    
    # Countries
    path('countries/', country_list, name='country_list'),
]

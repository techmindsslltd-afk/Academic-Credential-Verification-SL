"""
URL configuration for verifications app
"""
from django.urls import path
from .views import (
    VerificationLogListView, VerificationStatsView,
    VerificationReportListView, FraudAlertListView, FraudAlertResolveView
)

urlpatterns = [
    path('logs/', VerificationLogListView.as_view(), name='verification_logs'),
    path('stats/', VerificationStatsView.as_view(), name='verification_stats'),
    path('reports/', VerificationReportListView.as_view(), name='verification_reports'),
    path('fraud-alerts/', FraudAlertListView.as_view(), name='fraud_alerts'),
    path('fraud-alerts/<uuid:id>/resolve/', FraudAlertResolveView.as_view(), name='fraud_alert_resolve'),
]

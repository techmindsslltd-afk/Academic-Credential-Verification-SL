"""
Views for verifications
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from .models import VerificationLog, VerificationReport, FraudAlert, VerificationResult
from .serializers import (
    VerificationLogSerializer, VerificationReportSerializer,
    FraudAlertSerializer, VerificationStatsSerializer
)
from apps.accounts.permissions import IsSuperAdmin, IsSuperAdminOrInstitutionAdmin
from apps.accounts.models import UserRole


class VerificationLogListView(generics.ListAPIView):
    """List verification logs"""
    serializer_class = VerificationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['method', 'result']
    search_fields = ['credential_id_searched', 'verifier_email']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == UserRole.SUPER_ADMIN:
            return VerificationLog.objects.all()
        elif user.role == UserRole.INSTITUTION_ADMIN:
            try:
                institution = user.institution_admin_profile.institution
                return VerificationLog.objects.filter(
                    credential__institution=institution
                )
            except:
                return VerificationLog.objects.none()
        elif user.role == UserRole.EMPLOYER:
            return VerificationLog.objects.filter(verifier=user)
        elif user.role == UserRole.STUDENT:
            return VerificationLog.objects.filter(credential__holder=user)
        
        return VerificationLog.objects.none()


class VerificationStatsView(APIView):
    """Get verification statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        # Base queryset based on role
        if user.role == UserRole.SUPER_ADMIN:
            qs = VerificationLog.objects.all()
        elif user.role == UserRole.INSTITUTION_ADMIN:
            try:
                institution = user.institution_admin_profile.institution
                qs = VerificationLog.objects.filter(credential__institution=institution)
            except:
                qs = VerificationLog.objects.none()
        elif user.role == UserRole.EMPLOYER:
            qs = VerificationLog.objects.filter(verifier=user)
        else:
            qs = VerificationLog.objects.filter(credential__holder=user)
        
        stats = {
            'total_verifications': qs.count(),
            'valid_count': qs.filter(result=VerificationResult.VALID).count(),
            'invalid_count': qs.filter(result=VerificationResult.INVALID).count(),
            'revoked_count': qs.filter(result=VerificationResult.REVOKED).count(),
            'today_count': qs.filter(created_at__date=today).count(),
            'this_month_count': qs.filter(created_at__date__gte=month_start).count(),
        }
        
        return Response(stats)


class VerificationReportListView(generics.ListAPIView):
    """List verification reports"""
    serializer_class = VerificationReportSerializer
    permission_classes = [IsSuperAdmin]
    
    def get_queryset(self):
        return VerificationReport.objects.all()


class FraudAlertListView(generics.ListAPIView):
    """List fraud alerts"""
    serializer_class = FraudAlertSerializer
    permission_classes = [IsSuperAdminOrInstitutionAdmin]
    filterset_fields = ['alert_type', 'severity', 'is_resolved']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == UserRole.SUPER_ADMIN:
            return FraudAlert.objects.all()
        try:
            institution = user.institution_admin_profile.institution
            return FraudAlert.objects.filter(institution=institution)
        except:
            return FraudAlert.objects.none()


class FraudAlertResolveView(APIView):
    """Resolve a fraud alert"""
    permission_classes = [IsSuperAdminOrInstitutionAdmin]
    
    def post(self, request, id):
        try:
            alert = FraudAlert.objects.get(id=id)
            
            if alert.is_resolved:
                return Response(
                    {'error': 'Alert is already resolved'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            alert.is_resolved = True
            alert.resolved_by = request.user
            alert.resolved_at = timezone.now()
            alert.resolution_notes = request.data.get('notes', '')
            alert.save()
            
            return Response({'message': 'Alert resolved successfully'})
            
        except FraudAlert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )

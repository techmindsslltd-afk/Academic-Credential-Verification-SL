"""
Views for accreditation and WHED lookup
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from .models import AccreditationBody, WHEDRecord, AccreditationLookupLog
from .serializers import (
    AccreditationBodySerializer, WHEDRecordSerializer,
    AccreditationLookupLogSerializer
)
from apps.accounts.permissions import IsSuperAdmin


class AccreditationBodyListView(generics.ListAPIView):
    """List accreditation bodies"""
    serializer_class = AccreditationBodySerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['country', 'body_type', 'is_recognized']
    search_fields = ['name', 'short_name', 'country']
    
    def get_queryset(self):
        return AccreditationBody.objects.all()


class AccreditationBodyDetailView(generics.RetrieveAPIView):
    """Get accreditation body details"""
    serializer_class = AccreditationBodySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    queryset = AccreditationBody.objects.all()


class WHEDSearchView(APIView):
    """Search WHED database"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        country = request.query_params.get('country', '')
        whed_id = request.query_params.get('whed_id', '')
        
        if not query and not country and not whed_id:
            return Response({
                'error': 'Please provide search query, country, or WHED ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        records = WHEDRecord.objects.all()
        
        if whed_id:
            records = records.filter(whed_id__iexact=whed_id)
            search_type = 'whed_id'
        elif query:
            records = records.filter(
                Q(institution_name__icontains=query) |
                Q(institution_name_local__icontains=query) |
                Q(city__icontains=query)
            )
            search_type = 'institution_name'
        
        if country:
            records = records.filter(
                Q(country__icontains=country) |
                Q(country_code__iexact=country)
            )
            if not query and not whed_id:
                search_type = 'country'
        
        # Limit results
        records = records[:100]
        
        # Log the lookup
        if request.user.is_authenticated:
            AccreditationLookupLog.objects.create(
                search_query=query or whed_id or country,
                search_type=search_type,
                results_count=records.count(),
                user=request.user,
                ip_address=self.get_client_ip(request)
            )
        
        serializer = WHEDRecordSerializer(records, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class WHEDRecordDetailView(generics.RetrieveAPIView):
    """Get WHED record details"""
    serializer_class = WHEDRecordSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'whed_id'
    queryset = WHEDRecord.objects.all()


class AccreditationLookupLogListView(generics.ListAPIView):
    """List accreditation lookup logs (Super Admin only)"""
    serializer_class = AccreditationLookupLogSerializer
    permission_classes = [IsSuperAdmin]
    
    def get_queryset(self):
        return AccreditationLookupLog.objects.select_related('user', 'whed_record')


# Country list for filtering
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def country_list(request):
    """Get list of countries with institutions"""
    countries = WHEDRecord.objects.values('country', 'country_code').distinct().order_by('country')
    return Response(list(countries))

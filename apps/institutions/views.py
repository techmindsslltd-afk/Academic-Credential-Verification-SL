"""
Views for institutions
"""
import json
from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.db import transaction

from .models import Institution, Program, AccreditationRecord, InstitutionType
from .serializers import (
    InstitutionListSerializer, InstitutionDetailSerializer,
    InstitutionCreateSerializer, ProgramSerializer, AccreditationRecordSerializer
)
from apps.accounts.permissions import IsSuperAdmin, IsSuperAdminOrInstitutionAdmin


class InstitutionListView(generics.ListAPIView):
    """List all institutions"""
    serializer_class = InstitutionListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Only include non-choice fields in filterset_fields to avoid django-filters compatibility issues
    filterset_fields = ['country', 'is_partner', 'is_verified']
    search_fields = ['name', 'short_name', 'whed_id', 'city']
    ordering_fields = ['name', 'created_at', 'total_credentials_issued']
    
    def get_queryset(self):
        queryset = Institution.objects.filter(is_active=True).annotate(
            program_count=Count('programs')
        )
        
        # Manually filter by institution_type and accreditation_status if provided
        institution_type = self.request.query_params.get('institution_type', None)
        if institution_type:
            queryset = queryset.filter(institution_type=institution_type)
        
        accreditation_status = self.request.query_params.get('accreditation_status', None)
        if accreditation_status:
            queryset = queryset.filter(accreditation_status=accreditation_status)
        
        return queryset


class InstitutionDetailView(generics.RetrieveAPIView):
    """Get institution details"""
    serializer_class = InstitutionDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Institution.objects.prefetch_related('programs', 'accreditation_history')


class InstitutionCreateView(generics.CreateAPIView):
    """Create a new institution (Super Admin only)"""
    serializer_class = InstitutionCreateSerializer
    permission_classes = [IsSuperAdmin]
    
    def perform_create(self, serializer):
        serializer.save(accreditation_status='pending')


class InstitutionUpdateView(generics.UpdateAPIView):
    """Update an institution"""
    serializer_class = InstitutionDetailSerializer
    permission_classes = [IsSuperAdminOrInstitutionAdmin]
    lookup_field = 'id'
    queryset = Institution.objects.all()


class InstitutionDeleteView(generics.DestroyAPIView):
    """Delete an institution (Super Admin only)"""
    permission_classes = [IsSuperAdmin]
    lookup_field = 'id'
    queryset = Institution.objects.all()


class ProgramListView(generics.ListCreateAPIView):
    """List or create programs"""
    serializer_class = ProgramSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['institution', 'degree_level', 'is_active']
    search_fields = ['name', 'code', 'department']
    
    def get_queryset(self):
        return Program.objects.select_related('institution')
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdminOrInstitutionAdmin()]
        return super().get_permissions()


class ProgramDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a program"""
    serializer_class = ProgramSerializer
    permission_classes = [IsSuperAdminOrInstitutionAdmin]
    lookup_field = 'id'
    queryset = Program.objects.all()


class AccreditationRecordListView(generics.ListCreateAPIView):
    """List or create accreditation records"""
    serializer_class = AccreditationRecordSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['institution', 'status']
    
    def get_queryset(self):
        return AccreditationRecord.objects.select_related('institution')


# WHED Lookup endpoint
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def whed_lookup(request):
    """Search institutions by WHED ID or name"""
    query = request.query_params.get('q', '')
    country = request.query_params.get('country', '')
    
    if not query and not country:
        return Response({'error': 'Please provide search query or country'}, status=400)
    
    institutions = Institution.objects.filter(is_active=True)
    
    if query:
        institutions = institutions.filter(
            Q(name__icontains=query) |
            Q(whed_id__icontains=query) |
            Q(short_name__icontains=query)
        )
    
    if country:
        institutions = institutions.filter(country__icontains=country)
    
    serializer = InstitutionListSerializer(institutions[:50], many=True)
    return Response({
        'count': institutions.count(),
        'results': serializer.data
    })


class BulkUploadInstitutionsView(APIView):
    """Bulk upload institutions from world_universities_and_domains.json file"""
    permission_classes = [IsSuperAdmin]
    
    def post(self, request):
        try:
            # Check if file is uploaded
            if 'file' not in request.FILES:
                return Response(
                    {'error': 'No file uploaded. Please upload world_universities_and_domains.json file.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_file = request.FILES['file']
            
            # Validate file type
            if not uploaded_file.name.endswith('.json'):
                return Response(
                    {'error': 'Invalid file type. Please upload a JSON file.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Read and parse JSON
            try:
                file_content = uploaded_file.read().decode('utf-8')
                institutions_data = json.loads(file_content)
            except json.JSONDecodeError as e:
                return Response(
                    {'error': f'Invalid JSON format: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not isinstance(institutions_data, list):
                return Response(
                    {'error': 'JSON file must contain an array of institutions.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process institutions
            created_count = 0
            updated_count = 0
            skipped_count = 0
            errors = []
            
            with transaction.atomic():
                for idx, inst_data in enumerate(institutions_data):
                    try:
                        # Extract data from JSON
                        name = inst_data.get('name', '').strip()
                        if not name:
                            skipped_count += 1
                            continue
                        
                        # Get website (first web page if available)
                        website = ''
                        web_pages = inst_data.get('web_pages', [])
                        if web_pages and len(web_pages) > 0:
                            website = web_pages[0].strip()
                            if website:
                                # Ensure URL starts with http/https
                                if not website.startswith(('http://', 'https://')):
                                    website = f'https://{website}'
                                # Validate URL format (basic check)
                                if len(website) > 200:  # URLField max_length check
                                    website = website[:200]
                        
                        # Get country and country code
                        country = inst_data.get('country', '').strip()
                        country_code = inst_data.get('alpha_two_code', '').strip().upper()
                        
                        # Get city/state from state-province
                        state_province = inst_data.get('state-province')
                        city = state_province.strip() if state_province else ''
                        
                        # Generate short name (first 3-4 words or acronym)
                        short_name = self._generate_short_name(name)
                        
                        # Check if institution already exists (by name and country)
                        existing = Institution.objects.filter(
                            name__iexact=name,
                            country__iexact=country
                        ).first()
                        
                        if existing:
                            # Update existing institution if needed
                            if not existing.website and website:
                                existing.website = website
                            if not existing.country_code and country_code:
                                existing.country_code = country_code
                            if not existing.city and city:
                                existing.city = city
                            if not existing.short_name:
                                existing.short_name = short_name
                            existing.save()
                            updated_count += 1
                        else:
                            # Create new institution
                            Institution.objects.create(
                                name=name,
                                short_name=short_name,
                                website=website,
                                country=country,
                                country_code=country_code,
                                city=city,
                                institution_type=InstitutionType.UNIVERSITY,
                                accreditation_status='pending',
                                is_active=True,
                                is_verified=False,
                                is_partner=False
                            )
                            created_count += 1
                    
                    except Exception as e:
                        errors.append({
                            'index': idx + 1,
                            'name': inst_data.get('name', 'Unknown'),
                            'error': str(e)
                        })
                        skipped_count += 1
                        continue
            
            return Response({
                'message': 'Bulk upload completed',
                'summary': {
                    'total_processed': len(institutions_data),
                    'created': created_count,
                    'updated': updated_count,
                    'skipped': skipped_count,
                    'errors': len(errors)
                },
                'errors': errors[:50] if errors else []  # Limit errors to first 50
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Upload failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_short_name(self, full_name):
        """Generate a short name from full institution name"""
        # Remove common suffixes
        suffixes = ['University', 'College', 'Institute', 'School', 'Academy']
        words = full_name.split()
        
        # Try to create acronym from first letters
        if len(words) <= 4:
            return ' '.join(words[:3])
        
        # Create acronym from first letters of each word
        acronym = ''.join([word[0].upper() for word in words[:4] if word])
        return acronym if len(acronym) <= 10 else acronym[:10]

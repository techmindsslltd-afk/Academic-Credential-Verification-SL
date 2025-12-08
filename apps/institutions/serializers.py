"""
Serializers for institutions
"""
from rest_framework import serializers
from .models import Institution, Program, AccreditationRecord


class ProgramSerializer(serializers.ModelSerializer):
    """Serializer for academic programs"""
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    
    class Meta:
        model = Program
        fields = [
            'id', 'institution', 'institution_name', 'name', 'code',
            'degree_level', 'department', 'faculty', 'duration_years',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AccreditationRecordSerializer(serializers.ModelSerializer):
    """Serializer for accreditation records"""
    
    class Meta:
        model = AccreditationRecord
        fields = [
            'id', 'institution', 'accreditation_body', 'status',
            'granted_date', 'expiry_date', 'certificate_number',
            'notes', 'certificate_document', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class InstitutionListSerializer(serializers.ModelSerializer):
    """Serializer for institution list"""
    program_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Institution
        fields = [
            'id', 'name', 'short_name', 'institution_type', 'whed_id',
            'country', 'city', 'logo', 'accreditation_status',
            'is_partner', 'is_verified', 'program_count',
            'total_credentials_issued', 'total_students'
        ]


class InstitutionDetailSerializer(serializers.ModelSerializer):
    """Serializer for institution detail"""
    programs = ProgramSerializer(many=True, read_only=True)
    accreditation_history = AccreditationRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Institution
        fields = [
            'id', 'name', 'short_name', 'institution_type', 'whed_id',
            'website', 'email', 'phone', 'country', 'country_code',
            'city', 'address', 'logo', 'accreditation_status',
            'accreditation_body', 'accreditation_date', 'accreditation_expiry',
            'founded_year', 'is_partner', 'partner_since', 'is_active',
            'is_verified', 'blockchain_address', 'total_credentials_issued',
            'total_students', 'programs', 'accreditation_history',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InstitutionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating institutions"""
    
    class Meta:
        model = Institution
        fields = [
            'name', 'short_name', 'institution_type', 'whed_id',
            'website', 'email', 'phone', 'country', 'country_code',
            'city', 'address', 'logo', 'accreditation_body',
            'founded_year'
        ]

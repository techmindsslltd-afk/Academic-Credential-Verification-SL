"""
Serializers for accreditation
"""
from rest_framework import serializers
from .models import AccreditationBody, WHEDRecord, AccreditationLookupLog


class AccreditationBodySerializer(serializers.ModelSerializer):
    """Serializer for accreditation bodies"""
    
    class Meta:
        model = AccreditationBody
        fields = [
            'id', 'name', 'short_name', 'country', 'region',
            'body_type', 'website', 'email', 'phone',
            'is_recognized', 'recognized_by', 'description',
            'created_at', 'updated_at'
        ]


class WHEDRecordSerializer(serializers.ModelSerializer):
    """Serializer for WHED records"""
    is_partner = serializers.SerializerMethodField()
    
    class Meta:
        model = WHEDRecord
        fields = [
            'id', 'whed_id', 'institution_name', 'institution_name_local',
            'country', 'country_code', 'city', 'address',
            'website', 'email', 'phone', 'institution_type',
            'founded_year', 'is_accredited', 'accreditation_body',
            'is_partner', 'last_updated', 'data_source'
        ]
    
    def get_is_partner(self, obj):
        return obj.linked_institution is not None


class AccreditationLookupLogSerializer(serializers.ModelSerializer):
    """Serializer for lookup logs"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = AccreditationLookupLog
        fields = [
            'id', 'search_query', 'search_type', 'results_count',
            'whed_record', 'user', 'user_email', 'ip_address', 'created_at'
        ]

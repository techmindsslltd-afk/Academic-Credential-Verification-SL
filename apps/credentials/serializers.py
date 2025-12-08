"""
Serializers for credentials
"""
from rest_framework import serializers
from .models import Credential, CredentialShare, CredentialBatch, BlockchainTransaction


class CredentialListSerializer(serializers.ModelSerializer):
    """Serializer for credential list"""
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    holder_email = serializers.CharField(source='holder.email', read_only=True)
    
    class Meta:
        model = Credential
        fields = [
            'id', 'credential_id', 'credential_type', 'status',
            'holder_name', 'holder_email', 'institution', 'institution_name',
            'program_name', 'degree_level', 'completion_date', 'issue_date',
            'blockchain_hash', 'created_at'
        ]


class CredentialDetailSerializer(serializers.ModelSerializer):
    """Serializer for credential detail"""
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    holder_email = serializers.CharField(source='holder.email', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.full_name', read_only=True)
    
    class Meta:
        model = Credential
        fields = [
            'id', 'credential_id', 'credential_type', 'status',
            'holder', 'holder_name', 'holder_email', 'holder_student_id',
            'holder_date_of_birth', 'institution', 'institution_name',
            'program', 'program_name', 'degree_level', 'major', 'minor',
            'specialization', 'grade', 'honors', 'credits_earned',
            'enrollment_date', 'completion_date', 'issue_date', 'expiry_date',
            'blockchain_hash', 'blockchain_tx_id', 'block_number', 'ipfs_hash',
            'document', 'document_hash', 'qr_code', 'verification_url',
            'issued_by', 'issued_by_name', 'revoked_at', 'revocation_reason',
            'metadata', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'credential_id', 'blockchain_hash', 'blockchain_tx_id',
            'block_number', 'document_hash', 'qr_code', 'verification_url',
            'created_at', 'updated_at'
        ]


class CredentialCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating credentials"""
    
    class Meta:
        model = Credential
        fields = [
            'credential_type', 'holder', 'holder_name', 'holder_student_id',
            'holder_date_of_birth', 'institution', 'program', 'program_name',
            'degree_level', 'major', 'minor', 'specialization', 'grade',
            'honors', 'credits_earned', 'enrollment_date', 'completion_date',
            'issue_date', 'expiry_date', 'document', 'metadata', 'notes'
        ]


class CredentialVerifySerializer(serializers.Serializer):
    """Serializer for credential verification request"""
    credential_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    blockchain_hash = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    def validate_credential_id(self, value):
        """Strip whitespace from credential_id"""
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            return value if value else None
        return str(value).strip() if value else None
    
    def validate_blockchain_hash(self, value):
        """Strip whitespace from blockchain_hash"""
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            return value if value else None
        return str(value).strip() if value else None
    
    def validate(self, attrs):
        credential_id = attrs.get('credential_id')
        blockchain_hash = attrs.get('blockchain_hash')
        
        # Ensure both are either None or non-empty strings
        if credential_id is not None and not credential_id:
            credential_id = None
        if blockchain_hash is not None and not blockchain_hash:
            blockchain_hash = None
        
        # Check if both are empty/None
        if not credential_id and not blockchain_hash:
            raise serializers.ValidationError(
                'Either credential_id or blockchain_hash is required'
            )
        
        # Update attrs with cleaned values
        attrs['credential_id'] = credential_id
        attrs['blockchain_hash'] = blockchain_hash
        
        return attrs


class CredentialShareSerializer(serializers.ModelSerializer):
    """Serializer for credential sharing"""
    expires_in_days = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    credential = serializers.PrimaryKeyRelatedField(queryset=Credential.objects.all())
    
    class Meta:
        model = CredentialShare
        fields = [
            'id', 'credential', 'share_token', 'shared_with_email',
            'shared_with_company', 'is_active', 'expires_at', 'max_views',
            'view_count', 'hide_grade', 'hide_student_id', 'created_at',
            'expires_in_days'
        ]
        read_only_fields = ['id', 'share_token', 'view_count', 'created_at']
    
    def validate(self, attrs):
        """Validate and process expires_in_days"""
        expires_in_days = attrs.pop('expires_in_days', None)
        if expires_in_days is not None and expires_in_days > 0:
            from django.utils import timezone
            from datetime import timedelta
            attrs['expires_at'] = timezone.now() + timedelta(days=expires_in_days)
        return attrs


class CredentialBatchSerializer(serializers.ModelSerializer):
    """Serializer for credential batches"""
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = CredentialBatch
        fields = [
            'id', 'institution', 'institution_name', 'name', 'description',
            'status', 'total_count', 'processed_count', 'failed_count',
            'source_file', 'created_by', 'created_by_name',
            'created_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'status', 'total_count', 'processed_count', 'failed_count',
            'created_at', 'completed_at'
        ]


class BlockchainTransactionSerializer(serializers.ModelSerializer):
    """Serializer for blockchain transactions"""
    
    class Meta:
        model = BlockchainTransaction
        fields = [
            'id', 'credential', 'transaction_type', 'transaction_hash',
            'block_number', 'gas_used', 'is_confirmed', 'confirmations',
            'created_at', 'confirmed_at'
        ]
        read_only_fields = ['id', 'created_at', 'confirmed_at']

"""
Serializers for user accounts
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, UserRole, StudentProfile, InstitutionAdminProfile,
    EmployerProfile, ActivityLog
)


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'avatar', 'role', 'is_active', 'is_verified',
            'email_verified', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'is_verified']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    institution_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    # Employer fields
    company_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    company_address = serializers.CharField(write_only=True, required=False, allow_blank=True)
    company_phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'first_name',
            'last_name', 'phone', 'role', 'institution_id',
            'company_name', 'company_address', 'company_phone'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match'})
        
        role = attrs.get('role')
        institution_id = attrs.get('institution_id')
        
        # Validate institution selection for students and institution admins
        if role in [UserRole.STUDENT, UserRole.INSTITUTION_ADMIN]:
            if not institution_id:
                raise serializers.ValidationError({
                    'institution_id': 'Institution selection is required for this role'
                })
            
            # For students, verify it's a partner institution
            if role == UserRole.STUDENT:
                from apps.institutions.models import Institution
                try:
                    institution = Institution.objects.get(id=institution_id)
                    if not institution.is_partner:
                        raise serializers.ValidationError({
                            'institution_id': 'Students can only select partner institutions'
                        })
                except Institution.DoesNotExist:
                    raise serializers.ValidationError({
                        'institution_id': 'Selected institution does not exist'
                    })
        
        # Validate employer fields
        if role == UserRole.EMPLOYER:
            if not attrs.get('company_name'):
                raise serializers.ValidationError({
                    'company_name': 'Company name is required for employers'
                })
        
        return attrs
    
    def create(self, validated_data):
        password_confirm = validated_data.pop('password_confirm')
        institution_id = validated_data.pop('institution_id', None)
        company_name = validated_data.pop('company_name', None)
        company_address = validated_data.pop('company_address', None)
        company_phone = validated_data.pop('company_phone', None)
        role = validated_data.get('role')
        
        user = User.objects.create_user(**validated_data)
        
        # Create appropriate profile based on role
        if role == UserRole.STUDENT and institution_id:
            from apps.institutions.models import Institution
            try:
                institution = Institution.objects.get(id=institution_id)
                StudentProfile.objects.create(
                    user=user,
                    institution=institution
                )
            except Institution.DoesNotExist:
                pass  # Institution validation already done
        
        elif role == UserRole.INSTITUTION_ADMIN and institution_id:
            from apps.institutions.models import Institution
            try:
                institution = Institution.objects.get(id=institution_id)
                InstitutionAdminProfile.objects.create(
                    user=user,
                    institution=institution
                )
            except Institution.DoesNotExist:
                pass  # Institution validation already done
        
        elif role == UserRole.EMPLOYER:
            EmployerProfile.objects.create(
                user=user,
                company_name=company_name or '',
                company_address=company_address or '',
                company_phone=company_phone or ''
            )
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )
            if not user:
                raise serializers.ValidationError('Invalid email or password')
            if not user.is_active:
                raise serializers.ValidationError('Account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must provide email and password')
        
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect')
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match'})
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match'})
        return attrs


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for student profile"""
    user = UserSerializer(read_only=True)
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'student_id', 'date_of_birth', 'nationality',
            'address', 'institution', 'institution_name', 'program',
            'enrollment_date', 'graduation_date', 'wallet_address',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InstitutionAdminProfileSerializer(serializers.ModelSerializer):
    """Serializer for institution admin profile"""
    user = UserSerializer(read_only=True)
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    
    class Meta:
        model = InstitutionAdminProfile
        fields = [
            'id', 'user', 'institution', 'institution_name', 'department',
            'position', 'employee_id', 'can_issue_credentials',
            'can_revoke_credentials', 'can_manage_students', 'can_manage_staff',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployerProfileSerializer(serializers.ModelSerializer):
    """Serializer for employer profile"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = EmployerProfile
        fields = [
            'id', 'user', 'company_name', 'company_website', 'company_logo',
            'industry', 'company_size', 'company_address', 'company_phone',
            'monthly_verification_limit', 'verifications_this_month',
            'api_key', 'api_enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'api_key', 'verifications_this_month', 'created_at', 'updated_at']


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for activity logs"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'user_email', 'action', 'description',
            'ip_address', 'user_agent', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

"""
User models with role-based authentication for CertChain
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    """User role choices"""
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    INSTITUTION_ADMIN = 'institution_admin', 'Institution Admin'
    STUDENT = 'student', 'Student'
    EMPLOYER = 'employer', 'Employer/Verifier'


class UserManager(BaseUserManager):
    """Custom user manager"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', UserRole.SUPER_ADMIN)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with role-based access"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    
    # Profile fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Role and permissions
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT
    )
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Security
    failed_login_attempts = models.PositiveIntegerField(default=0)
    lockout_until = models.DateTimeField(blank=True, null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_super_admin(self):
        return self.role == UserRole.SUPER_ADMIN
    
    def is_institution_admin(self):
        return self.role == UserRole.INSTITUTION_ADMIN
    
    def is_student(self):
        return self.role == UserRole.STUDENT
    
    def is_employer(self):
        return self.role == UserRole.EMPLOYER


class StudentProfile(models.Model):
    """Extended profile for students"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_id = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    
    # Academic info
    institution = models.ForeignKey(
        'institutions.Institution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    program = models.CharField(max_length=200, blank=True)
    enrollment_date = models.DateField(blank=True, null=True)
    graduation_date = models.DateField(blank=True, null=True)
    
    # Wallet for credentials
    wallet_address = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
    
    def __str__(self):
        return f"Student: {self.user.full_name}"


class InstitutionAdminProfile(models.Model):
    """Extended profile for institution administrators"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='institution_admin_profile'
    )
    institution = models.ForeignKey(
        'institutions.Institution',
        on_delete=models.CASCADE,
        related_name='admins'
    )
    department = models.CharField(max_length=200, blank=True)
    position = models.CharField(max_length=200, blank=True)
    employee_id = models.CharField(max_length=50, blank=True)
    
    # Permissions within institution
    can_issue_credentials = models.BooleanField(default=True)
    can_revoke_credentials = models.BooleanField(default=False)
    can_manage_students = models.BooleanField(default=True)
    can_manage_staff = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Institution Admin Profile'
        verbose_name_plural = 'Institution Admin Profiles'
    
    def __str__(self):
        return f"Admin: {self.user.full_name} @ {self.institution.name}"


class EmployerProfile(models.Model):
    """Extended profile for employers/verifiers"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employer_profile'
    )
    company_name = models.CharField(max_length=200)
    company_website = models.URLField(blank=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    
    # Contact info
    company_address = models.TextField(blank=True)
    company_phone = models.CharField(max_length=20, blank=True)
    
    # Verification quota
    monthly_verification_limit = models.PositiveIntegerField(default=100)
    verifications_this_month = models.PositiveIntegerField(default=0)
    
    # API access
    api_key = models.CharField(max_length=100, blank=True, unique=True, null=True)
    api_enabled = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Employer Profile'
        verbose_name_plural = 'Employer Profiles'
    
    def __str__(self):
        return f"Employer: {self.company_name}"


class EmailVerificationToken(models.Model):
    """Token for email verification"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()


class PasswordResetToken(models.Model):
    """Token for password reset"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()


class ActivityLog(models.Model):
    """User activity logging"""
    
    class ActionType(models.TextChoices):
        LOGIN = 'login', 'Login'
        LOGOUT = 'logout', 'Logout'
        PASSWORD_CHANGE = 'password_change', 'Password Change'
        PROFILE_UPDATE = 'profile_update', 'Profile Update'
        CREDENTIAL_ISSUED = 'credential_issued', 'Credential Issued'
        CREDENTIAL_VERIFIED = 'credential_verified', 'Credential Verified'
        CREDENTIAL_REVOKED = 'credential_revoked', 'Credential Revoked'
        API_ACCESS = 'api_access', 'API Access'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ActionType.choices)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.created_at}"

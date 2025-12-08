"""
Views for user authentication and profiles
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import logout, login, authenticate
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.conf import settings
import json
import uuid

from .models import (
    User, UserRole, StudentProfile, InstitutionAdminProfile,
    EmployerProfile, EmailVerificationToken, PasswordResetToken, ActivityLog
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, StudentProfileSerializer,
    InstitutionAdminProfileSerializer, EmployerProfileSerializer,
    ActivityLogSerializer
)
from .permissions import IsSuperAdmin, IsOwnerOrSuperAdmin


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create email verification token
        token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # TODO: Send verification email
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Registration successful. Please verify your email.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginPageView(View):
    """Traditional login page view - handles both HTML and JSON requests"""
    def get(self, request):
        # If already logged in, redirect to dashboard or next
        if request.user.is_authenticated:
            next_url = request.GET.get('next', '/dashboard')
            return redirect(next_url)
        
        return render(request, 'accounts/login-page.html', {
            'next': request.GET.get('next', '/dashboard')
        })
    
    def post(self, request):
        # Check if this is a JSON/AJAX request
        is_json_request = (
            request.content_type == 'application/json' or
            request.META.get('HTTP_ACCEPT', '').find('application/json') != -1 or
            request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
        )
        
        # If already logged in, redirect
        if request.user.is_authenticated:
            if is_json_request:
                return JsonResponse({
                    'message': 'Already logged in',
                    'user': UserSerializer(request.user).data
                }, status=200)
            next_url = request.POST.get('next', request.GET.get('next', '/dashboard'))
            return redirect(next_url)
        
        # Handle JSON requests (from modal)
        if is_json_request:
            try:
                if request.content_type == 'application/json':
                    data = json.loads(request.body)
                else:
                    data = request.POST
                
                email = data.get('email')
                password = data.get('password')
                
                if not email or not password:
                    return JsonResponse({
                        'error': 'Please provide both email and password',
                        'email': ['This field is required.'],
                        'password': ['This field is required.']
                    }, status=400)
                
                # Use LoginSerializer for validation
                serializer = LoginSerializer(data={'email': email, 'password': password}, context={'request': request})
                if not serializer.is_valid():
                    return JsonResponse(serializer.errors, status=400)
                
                user = serializer.validated_data['user']
                
                # Update last login
                user.last_login = timezone.now()
                user.failed_login_attempts = 0
                user.save(update_fields=['last_login', 'failed_login_attempts'])
                
                # Log activity
                ip_address = self.get_client_ip(request)
                ActivityLog.objects.create(
                    user=user,
                    action=ActivityLog.ActionType.LOGIN,
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Create Django session for traditional authentication
                login(request, user)
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                # Get profile data based on role
                profile_data = self.get_profile_data(user)
                
                return JsonResponse({
                    'message': 'Login successful',
                    'user': UserSerializer(user).data,
                    'profile': profile_data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=200)
            except Exception as e:
                import traceback
                print(f"JSON login error: {str(e)}")
                print(traceback.format_exc())
                return JsonResponse({
                    'error': 'Login failed',
                    'message': str(e)
                }, status=400)
        
        # Handle traditional form POST (HTML)
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '/dashboard')
        
        if not email or not password:
            return render(request, 'accounts/login-page.html', {
                'error': 'Please provide both email and password',
                'next': next_url,
                'email': email
            })
        
        # Authenticate user
        # Note: BruteBuster decorator expects 'email' in kwargs, but Django authenticate uses 'username'
        # We need to pass 'email' as well so BruteBuster can track failed attempts
        try:
            # Pass both username and email - username for Django auth, email for BruteBuster
            user = authenticate(request, username=email, password=password, email=email)
            
            # Check if authenticate returned a redirect response (e.g., from brute force protection)
            if isinstance(user, HttpResponseRedirect):
                # This happens when BruteBuster doesn't find 'email' in kwargs and redirects
                # Instead of redirecting, show an error message
                error_msg = 'Invalid email or password. Please try again.'
                try:
                    from apps.brutebuster.models import FailedAttempt
                    ip_address = self.get_client_ip(request)
                    failed_attempt = FailedAttempt.objects.filter(email=email, IP=ip_address).first()
                    if failed_attempt and hasattr(failed_attempt, 'too_many_failures') and failed_attempt.too_many_failures():
                        # Calculate block interval (timezone and timedelta already imported at top)
                        block_interval = getattr(settings, 'BB_BLOCK_INTERVAL', 15)
                        error_msg = f'Too many failed login attempts. Please try again after {block_interval} minutes.'
                except Exception as e:
                    # If brutebuster check fails, use default error message
                    pass
                
                return render(request, 'accounts/login-page.html', {
                    'error': error_msg,
                    'next': next_url,
                    'email': email
                })
        except Exception as e:
            # Handle any exceptions during authentication
            import traceback
            print(f"Authentication exception: {str(e)}")
            print(traceback.format_exc())
            return render(request, 'accounts/login-page.html', {
                'error': f'Authentication error: {str(e)}',
                'next': next_url,
                'email': email
            })
        
        # Check if user is None or not a user object
        if user is None:
            # Check if there's a brute force block message
            error_msg = 'Invalid email or password. Please try again.'
            try:
                from apps.brutebuster.models import FailedAttempt
                ip_address = self.get_client_ip(request)
                failed_attempt = FailedAttempt.objects.filter(email=email, IP=ip_address).first()
                if failed_attempt and hasattr(failed_attempt, 'too_many_failures') and failed_attempt.too_many_failures():
                    block_interval = failed_attempt.block_interval() if hasattr(failed_attempt, 'block_interval') else 15
                    error_msg = f'Too many failed login attempts. Please try again after {block_interval} minutes.'
            except Exception as e:
                # If brutebuster check fails, use default error message
                error_msg = 'Invalid email or password. Please try again.'
            
            return render(request, 'accounts/login-page.html', {
                'error': error_msg,
                'next': next_url,
                'email': email
            })
        
        # Now we know user is a User object, check if active
        if not user.is_active:
            return render(request, 'accounts/login-page.html', {
                'error': 'Your account is inactive. Please contact support.',
                'next': next_url,
                'email': email
            })
        
        # User is valid and active, proceed with login
        login(request, user)
        
        # Update last login
        user.last_login = timezone.now()
        user.failed_login_attempts = 0
        user.save(update_fields=['last_login', 'failed_login_attempts'])
        
        # Log activity
        ip_address = self.get_client_ip(request)
        ActivityLog.objects.create(
            user=user,
            action=ActivityLog.ActionType.LOGIN,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Redirect to next URL or dashboard
        return redirect(next_url)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
    def get_profile_data(self, user):
        """Get profile data based on user role"""
        if user.role == UserRole.STUDENT:
            try:
                return StudentProfileSerializer(user.student_profile).data
            except:
                return None
        elif user.role == UserRole.INSTITUTION_ADMIN:
            try:
                return InstitutionAdminProfileSerializer(user.institution_admin_profile).data
            except:
                return None
        elif user.role == UserRole.EMPLOYER:
            try:
                return EmployerProfileSerializer(user.employer_profile).data
            except:
                return None
        return None


class LoginView(APIView):
    """User login endpoint (API)"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Update last login
        user.last_login = timezone.now()
        user.failed_login_attempts = 0
        user.save(update_fields=['last_login', 'failed_login_attempts'])
        
        # Log activity
        ActivityLog.objects.create(
            user=user,
            action=ActivityLog.ActionType.LOGIN,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Create Django session for traditional authentication (for dashboard access)
        login(request, user)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Get profile data based on role
        profile_data = self.get_profile_data(user)
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'profile': profile_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
    def get_profile_data(self, user):
        if user.role == UserRole.STUDENT:
            try:
                return StudentProfileSerializer(user.student_profile).data
            except:
                return None
        elif user.role == UserRole.INSTITUTION_ADMIN:
            try:
                return InstitutionAdminProfileSerializer(user.institution_admin_profile).data
            except:
                return None
        elif user.role == UserRole.EMPLOYER:
            try:
                return EmployerProfileSerializer(user.employer_profile).data
            except:
                return None
        return None


class LogoutView(APIView):
    """User logout endpoint"""
    permission_classes = [permissions.AllowAny]  # Allow logout even if session expired
    
    def perform_logout(self, request):
        """Common logout logic for both GET and POST"""
        try:
            # Handle JWT token blacklisting if refresh token is provided
            if hasattr(request, 'data') and request.data:
                refresh_token = request.data.get('refresh')
                if refresh_token:
                    try:
                        token = RefreshToken(refresh_token)
                        token.blacklist()
                    except:
                        pass  # Token might already be invalid
            
            # Log activity if user is authenticated
            if request.user.is_authenticated:
                try:
                    ActivityLog.objects.create(
                        user=request.user,
                        action=ActivityLog.ActionType.LOGOUT,
                        ip_address=self.get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                except:
                    pass
            
            # Clear Django session (for traditional authentication)
            logout(request)
        except Exception as e:
            # Even if there's an error, try to clear the session
            try:
                logout(request)
            except:
                pass
    
    def get(self, request):
        """Handle GET requests (direct logout link clicks) - redirect to home"""
        self.perform_logout(request)
        return redirect('home')
    
    def post(self, request):
        """Handle POST requests (AJAX logout) - return JSON response"""
        self.perform_logout(request)
        return Response({'message': 'Logout successful'})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get or update current user profile"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        user_data = self.get_serializer(user).data
        
        # Add role-specific profile
        profile_data = None
        if user.role == UserRole.STUDENT:
            try:
                profile_data = StudentProfileSerializer(user.student_profile).data
            except:
                pass
        elif user.role == UserRole.INSTITUTION_ADMIN:
            try:
                profile_data = InstitutionAdminProfileSerializer(user.institution_admin_profile).data
            except:
                pass
        elif user.role == UserRole.EMPLOYER:
            try:
                profile_data = EmployerProfileSerializer(user.employer_profile).data
            except:
                pass
        
        return Response({
            'user': user_data,
            'profile': profile_data
        })


class PasswordChangeView(APIView):
    """Change user password"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action=ActivityLog.ActionType.PASSWORD_CHANGE,
            ip_address=self.get_client_ip(request)
        )
        
        return Response({'message': 'Password changed successfully'})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class PasswordResetRequestView(APIView):
    """Request password reset"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            token = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=1)
            )
            # TODO: Send password reset email
        except User.DoesNotExist:
            pass  # Don't reveal if email exists
        
        return Response({
            'message': 'If the email exists, a password reset link has been sent.'
        })


class PasswordResetConfirmView(APIView):
    """Confirm password reset"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            token = PasswordResetToken.objects.get(
                token=serializer.validated_data['token']
            )
            if not token.is_valid():
                return Response(
                    {'error': 'Token is invalid or expired'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token.user.set_password(serializer.validated_data['new_password'])
            token.user.save()
            token.is_used = True
            token.save()
            
            return Response({'message': 'Password reset successful'})
        except PasswordResetToken.DoesNotExist:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class VerifyEmailView(APIView):
    """Verify user email"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, token):
        try:
            verification = EmailVerificationToken.objects.get(token=token)
            if not verification.is_valid():
                return Response(
                    {'error': 'Token is invalid or expired'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            verification.user.email_verified = True
            verification.user.save()
            verification.is_used = True
            verification.save()
            
            return Response({'message': 'Email verified successfully'})
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


# Admin Views for Super Admin
class UserListView(generics.ListAPIView):
    """List all users (Super Admin only)"""
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]
    filterset_fields = ['role', 'is_active', 'is_verified']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'last_login', 'email']
    
    def get_queryset(self):
        return User.objects.all()


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a user (Super Admin only)"""
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]
    queryset = User.objects.all()
    lookup_field = 'id'


class StudentProfileListView(generics.ListAPIView):
    """List all student profiles"""
    serializer_class = StudentProfileSerializer
    permission_classes = [IsSuperAdmin]
    filterset_fields = ['institution']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'student_id']
    
    def get_queryset(self):
        return StudentProfile.objects.select_related('user', 'institution')


class ActivityLogListView(generics.ListAPIView):
    """List activity logs"""
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['action']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return ActivityLog.objects.all()
        return ActivityLog.objects.filter(user=user)


class ChangeUserRoleView(APIView):
    """Change user role"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        new_role = request.data.get('role')
        if not new_role:
            return Response(
                {'error': 'Role is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Map frontend role keys to backend role values
        role_map = {
            'super-admin': UserRole.SUPER_ADMIN,
            'institution-admin': UserRole.INSTITUTION_ADMIN,
            'student': UserRole.STUDENT,
            'employer': UserRole.EMPLOYER,
        }
        
        if new_role not in role_map:
            return Response(
                {'error': f'Invalid role: {new_role}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update user role
        user = request.user
        old_role = user.role
        user.role = role_map[new_role]
        user.save(update_fields=['role'])
        
        # Log activity
        try:
            ActivityLog.objects.create(
                user=user,
                action=ActivityLog.ActionType.PROFILE_UPDATE,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                description=f'Role changed from {old_role} to {user.role}'
            )
        except:
            pass
        
        # Return updated user data
        return Response({
            'message': f'Role changed to {user.get_role_display()}',
            'user': UserSerializer(user).data
        })
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

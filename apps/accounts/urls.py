"""
URL configuration for accounts app
"""
from django.urls import path
from .views import (
    RegisterView, LoginView, LoginPageView, LogoutView, ProfileView,
    PasswordChangeView, PasswordResetRequestView, PasswordResetConfirmView,
    VerifyEmailView, UserListView, UserDetailView, StudentProfileListView,
    ActivityLogListView, ChangeUserRoleView
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('api/login/', LoginView.as_view(), name='api_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Development only - Change user role
    path('change-role/', ChangeUserRoleView.as_view(), name='change_role'),
    
    # Password management
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Email verification
    path('verify-email/<uuid:token>/', VerifyEmailView.as_view(), name='verify_email'),
    
    # Admin endpoints
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<uuid:id>/', UserDetailView.as_view(), name='user_detail'),
    path('students/', StudentProfileListView.as_view(), name='student_list'),
    path('activity-logs/', ActivityLogListView.as_view(), name='activity_logs'),
]

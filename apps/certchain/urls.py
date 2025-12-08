"""
CertChain URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/institutions/', include('institutions.urls')),
    path('api/v1/credentials/', include('credentials.urls')),
    path('api/v1/verifications/', include('verifications.urls')),
    path('api/v1/accreditation/', include('accreditation.urls')),
    
    # JWT Token Refresh
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

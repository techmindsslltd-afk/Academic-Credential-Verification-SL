from django.contrib import admin
from django.urls import path, include

from django.urls import path, re_path, include  # add this
from django.conf import settings
from django.conf.urls.static import static
from apps.home import views

urlpatterns = [
    path('danger/', admin.site.urls),  # Django admin route
    
    # API v1 routes (for REST API)
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/institutions/', include('apps.institutions.urls')),
    path('api/v1/credentials/', include('apps.credentials.urls')),
    path('api/v1/verifications/', include('apps.verifications.urls')),
    path('api/v1/accreditation/', include('apps.accreditation.urls')),
    
    # Regular routes (for web pages)
    path("", include("apps.accounts.urls")),  # Auth routes - login / register
    path("", include("apps.home.urls")),
    path("", include("apps.staff.urls")),
    
    path("institutions/", include('apps.institutions.urls')),
    path("credentials/", include("apps.credentials.urls")),  # Credentials at /credentials/*
    path("", include("apps.verifications.urls")),
    path("", include("apps.accreditation.urls")),
    
	#path("ckeditor5/", include('django_ckeditor_5.urls')),
 	path("session_security/",include('session_security.urls')),
	
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Catch-all route for HTML pages (must be last to not interfere with API routes)
urlpatterns += [
    # Matches any html file, but exclude API routes and specific API endpoints
    # Exclude: /api/*, /credentials/share*, /credentials/verify*, /institutions/bulk-upload*
    re_path(r'^(?!api/|/api/|credentials/share|/credentials/share|credentials/verify|/credentials/verify|institutions/bulk-upload|/institutions/bulk-upload).*', views.pages, name='pages'),
]

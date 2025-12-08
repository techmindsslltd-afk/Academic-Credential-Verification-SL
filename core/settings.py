# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present TechMinds SL Ltd
"""

import os
from decouple import config
from unipath import Path   
import datetime        
import logging

from datetime import timedelta
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('kr', 'Krio'),
    ('fr', 'French'),  # French
    ('es', 'Spanish'),  # Spanish
    ('de', 'German'),   # German
    ('it', 'Italian'),  # Italian
    ('pt', 'Portuguese'),  # Portuguese
    ('ar', 'Arabic'),   # Arabic
    ('zh', 'Chinese'),  # Chinese (Simplified)
    ('hi', 'Hindi'),    # Hindi
    # Add other languages as needed
]



# Ensure BASE_DIR is a Path objec
LANGUAGE_CODE = 'en'
# Define BASE_DIR using os.path
BASE_DIR2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Use os.path.join for constructing paths
LOCALE_PATHS = [
    os.path.join(BASE_DIR2, 'locale'),
]
# Application definition
DEFAULT_AUTO_FIELD='django.db.models.AutoField' 
AUTH_USER_MODEL = 'accounts.User'

# Jitsi JWT secret (use the one configured on your Jitsi server)
JITSI_SECRET = 'cxCcOI-W7M1o2Jy4hGz_6dLZpnrkPJVgYJH7wTz5ioQ='

# load production server from .env     


#ALLOWED_HOSTS = ['sierrahopesl.com', 'www.sierrahopesl.com', config('SERVER', default='66.29.138.4')]


ALLOWED_HOSTS = [ 'localhost','192.168.2.130','127.0.0.1:8000','192.168.1.130','127.0.0.1','192.168.1.119','192.168.2.100']


   

# Application definition

# ============================================================================
# SECURITY SETTINGS
# ============================================================================

# Session Security Settings
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Sessions expire when browser closes
SESSION_SECURITY_EXPIRE_AFTER = 3600  # Session expires after 1 hour of inactivity (in seconds)
SESSION_COOKIE_AGE = 3600  # Session cookie age in seconds (1 hour)
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie (XSS protection)
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS (requires SSL)
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection - prevents cross-site request forgery

# BruteBuster Configuration - Protection against brute force attacks
# BruteBuster automatically protects django.contrib.auth.authenticate() calls
# It tracks failed login attempts per (email, IP) combination
BB_MAX_FAILURES = 5  # Maximum failed login attempts before blocking (default: 3)
BB_BLOCK_INTERVAL = 15  # Block duration in minutes after max failures reached (default: 15)
# Note: Blocks are applied per (email, IP) combination, so legitimate users from different IPs are not affected

# possible options: 'sweetalert', 'sweetalert2' - default is 'sweetalert2'
SWEETIFY_SWEETALERT_LIBRARY = 'sweetalert2'

#RECAPTCHA_PUBLIC_KEY = "6LfvUDkeAAAAAL4bXPmQy2J3ZjgDL9cbv11THgp3"
#RECAPTCHA_PRIVATE_KEY = "6LfvUDkeAAAAABXL-ps1ZH9cX93DjafxxsP_zhcO"

logger = logging.getLogger('django')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for Site framework
    "django.contrib.humanize",
    #sub-apps
    'apps',
    'apps.accounts',
    'apps.brutebuster',
    'apps.home',
	'apps.staff',
      
    
    # Local apps
    'apps.institutions',
    'apps.credentials',
    'apps.verifications',
    'apps.accreditation',

	#library
    'sweetify',              
    'session_security',  
    "post_office", 
    'imagefield',    
	'audit_trail', 
    'channels',  
    'corsheaders',      
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',

   # 'dbbackup', 
    #'sslserver',
    #'django_ckeditor_5',
   # "ckeditor",
   # "ckeditor_uploader",
    
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}
#DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
#DBBACKUP_STORAGE_OPTIONS = {'location': '/core/backup/'}

CORS_ALLOW_ALL_ORIGINS = True
# Alternatively, specify the allowed origins
CORS_ALLOWED_ORIGINS = [
    "http://localhost:63238",
    # Add other trusted origins here
]
POST_OFFICE = {
    'TEMPLATE_ENGINE': 'post_office',
    'MAX_RETRIES': 5,  
    'RETRY_INTERVAL': datetime.timedelta(minutes=5),  
}
X_FRAME_OPTIONS = 'SAMEORIGIN'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Required for session management
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # User authentication
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',  # Session timeout management
    'corsheaders.middleware.CorsMiddleware',
    'apps.brutebuster.middleware.RequestMiddleware',  # BruteBuster: Provides request context for brute force protection 
    # 'apps.accounts.middleware.UpdateLastActivityMiddleware',  # TODO: Create this middleware if needed
    #'apps.accounts.middleware.UserHistoryMiddleware',
    #'apps.home.http_redirect_middleware.HttpRedirectMiddleware',
    #'apps.home.XFrameOptionsMiddleware.DisableXFrameOptionsMiddleware',
    #'apps.home.XFrameOptionsMiddleware.ContentSecurityPolicyMiddleware',

    'apps.home.middleware.DisableXFrameOptionsMiddleware',
    'apps.home.middleware.VisitorTrackingMiddleware',

    'django.middleware.locale.LocaleMiddleware',
    

]  

ROOT_URLCONF = 'core.urls'
SITE_ID = 1  # Required for django.contrib.sites
LOGIN_REDIRECT_URL = "dashboard"  # Route defined in home/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in home/urls.py
TEMPLATE_DIR = os.path.join(CORE_DIR, "apps/templates")  # ROOT dir for templates
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

  
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': { 
            'context_processors': [ 
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.home.context_processors.general_settings', 
                'apps.home.context_processors.mysignature',
                'apps.home.context_processors.sidebar_stats', 
            ],
        },
    },{
        'BACKEND': 'post_office.template.backends.post_office.PostOfficeTemplates',
        'APP_DIRS': True,
        'DIRS':  [TEMPLATE_DIR],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
            ]
        }
    }   
]          

WSGI_APPLICATION = 'core.wsgi.application'

# Database   
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        #'NAME': 'clinic_management',  
        'NAME': 'CertChain',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.  sierrahopesl_clinic
        'PASSWORD': '', 
        'HOST': 'localhost',      # Or an IP Address that your DB is hosted on
        'PORT': '3306',          
    }      
}

      

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql', 
       #'NAME': 'clinic_management',  
#        'NAME': 'sierrahopesl_clinic',                      # Or path to database file if using sqlite3.
#        'USER': 'sierrahopesl_clinic_portal',                      # Not used with sqlite3.
#        'PASSWORD': 'INow@?IyZTf7', 
#        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
#        'PORT': '3306',
 #   }
#}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/


#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = 'apps/static/'

# Extra places for collectstatic to find static files.
MEDIA_ROOT = os.path.join(BASE_DIR, '../media')
MEDIA_URL = '/media/'

STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'apps/static'),
)


NUMB_TURN_CREDENTIAL = config('NUMB_TURN_CREDENTIAL', default=None)
NUMB_TURN_USERNAME = config('NUMB_TURN_USERNAME', default=None)

ASGI_APPLICATION = 'core.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",  # Use Redis for production
    },
}
#############################################################

#############################################################
#############################################################
#############################################################
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True
#SECURE_SSL_REDIRECT = True

# CSRF Trusted Origins - Allow redirects from Monime payment gateway
# Note: Django will also check the request's host dynamically
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://appleofgod.org',
    'https://www.appleofgod.org',
    'https://api.monime.io',  # Monime API domain
    'https://monime.io',  # Monime domain
    'http://localhost',  # Allow localhost without port
    'https://localhost',  # Allow localhost with https
]

# Allow CSRF to work with null Origin (for redirects from payment gateways)
CSRF_USE_SESSIONS = False  # Use cookies instead of sessions for CSRF
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF cookie if needed
# Paths to the copied certificate and key files
#SECURE_SSL_CERT = '/core/certificate/cert.pem'
#SECURE_SSL_KEY = '/core/certificate/key.pem'
#############################################################

# Email settings for email account default


# settings.py

# Use console backend for testing (emails print to console)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Use SMTP backend for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587  # Use 587 for TLS
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False  # Ensure this is False if using TLS
EMAIL_HOST_USER = 'tdchsinfo@gmail.com'
EMAIL_HOST_PASSWORD = 'hcerpjroveukllar'  # Ensure this is correct
DEFAULT_FROM_EMAIL = 'tdchsinfo@gmail.com'
EMAIL_DEBUG = True

# Email timeout (prevents hanging)
EMAIL_TIMEOUT = 10


# SITE_URL is already defined above, no need to redefine
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'mail.tdchs.edu.sl' # host of your cPanel email server
# EMAIL_PORT = 465 # or any other port that your server uses
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'info@tdchs.edu.sl' # your cPanel email address
# DEFAULT_FROM_EMAIL = 'info@tdchs.edu.sl'
# EMAIL_HOST_PASSWORD = 'main@2024' # your email password


#############################################################
#############################################################




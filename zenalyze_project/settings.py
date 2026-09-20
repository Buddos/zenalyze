"""
Django settings for Zenalyze Platform.
Converted from PHP to Python Django.
"""

from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / '.env')

# Add apps to sys.path
sys.path.insert(0, str(BASE_DIR / 'apps'))

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-zenalyze-mental-wellness-platform-2026-key')

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = ['*']

# CSRF trusted origins — required for Vercel / any HTTPS reverse-proxy
CSRF_TRUSTED_ORIGINS = [
    'https://zenalyze-six.vercel.app',
    'https://*.vercel.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Zenalyze Custom Apps
    'apps.accounts.apps.AccountsConfig',
    'apps.core.apps.CoreConfig',
    'apps.wellness.apps.WellnessConfig',
    'apps.community.apps.CommunityConfig',
    'apps.quotes.apps.QuotesConfig',
    'apps.therapists.apps.TherapistsConfig',
    'apps.administration.apps.AdministrationConfig',
    'apps.notifications.apps.NotificationsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zenalyze_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.theme_context',
                'apps.notifications.context_processors.notifications_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'zenalyze_project.wsgi.application'

# Database
# If DATABASE_URL is provided, connect to Supabase PostgreSQL.
# Otherwise, fall back gracefully to local SQLite for development.
DATABASE_URL = os.environ.get('DATABASE_URL')
SUPABASE_DB_PASSWORD = os.environ.get('SUPABASE_DB_PASSWORD')

if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif SUPABASE_DB_PASSWORD:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('SUPABASE_DB_NAME', 'postgres'),
            'USER': os.environ.get('SUPABASE_DB_USER', f"postgres.{os.environ.get('SUPABASE_PROJECT_ID', 'cpmjwdmjgkqxehjkvhgb')}"),
            'PASSWORD': SUPABASE_DB_PASSWORD,
            'HOST': os.environ.get('SUPABASE_DB_HOST', 'aws-1-eu-west-1.pooler.supabase.com'),
            'PORT': os.environ.get('SUPABASE_DB_PORT', '6543'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Supabase API Configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://cpmjwdmjgkqxehjkvhgb.supabase.co')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', os.environ.get('SUPABASE_PUBLISHABLE_KEY', 'sb_publishable_XVquVHtAOOOi5UDp9N2O7w_RZCHK4uS'))
SUPABASE_PROJECT_ID = os.environ.get('SUPABASE_PROJECT_ID', 'cpmjwdmjgkqxehjkvhgb')

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (User uploads, avatars, videos)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication URLs
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Session settings
# Use signed-cookie sessions so Vercel (read-only fs) doesn't need to write to the DB for sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_AGE = 1800      # 30-minute session timeout (matches legacy PHP)
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


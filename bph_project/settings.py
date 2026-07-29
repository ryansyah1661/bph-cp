import os
import ctypes
from pathlib import Path
from dotenv import load_dotenv

# Konfigurasi GDAL/GEOS untuk Windows (OSGeo4W)
if os.name == 'nt':
    os.environ['PATH'] = r'D:\OSGeo4W\bin' + os.pathsep + os.environ['PATH']
    os.environ['GDAL_LIBRARY_PATH'] = r'D:\OSGeo4W\bin\gdal313.dll'
    os.environ['GEOS_LIBRARY_PATH'] = r'D:\OSGeo4W\bin\geos_c.dll'
    GDAL_LIBRARY_PATH = r'D:\OSGeo4W\bin\gdal313.dll'
    GEOS_LIBRARY_PATH = r'D:\OSGeo4W\bin\geos_c.dll'

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key')

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'modeltranslation',  # Ditambahkan untuk multi-bahasa data database
    'core', 
    'widget_tweaks',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',  # Ditambahkan untuk GeoDjango
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Ditambahkan untuk sistem terjemahan Django i18n
    'core.middleware.LanguageSwitchMiddleware',   # Ditambahkan untuk switcher bahasa instan ?lang=id/en
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bph_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.unread_messages_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'bph_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # Diubah ke database spasial PostGIS
        'NAME': 'db_bph',
        'USER': 'postgres',
        'PASSWORD': 'ryan1602',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================
# KONFIGURASI BAHASA DAN ZONA WAKTU (WIB)
# =============================================================
LANGUAGE_CODE = 'id'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('id', 'Bahasa Indonesia'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================
# REDIRECTION ALUR LOGIN & LOGOUT CUSTOM ADMIN PANEL BPH
# =============================================================
LOGIN_URL = '/be/login/'
LOGIN_REDIRECT_URL = '/be/'
LOGOUT_REDIRECT_URL = '/be/login/'

# =============================================================
# KONFIGURASI KEAMANAN SESSION LOGIN
# =============================================================
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600

# =============================================================
# Konfigurasi SMTP Brevo untuk Notifikasi & Reset Password
# =============================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  
DEFAULT_FROM_EMAIL = 'Bhumi Pasa Hijau <no-reply@bhumipasahijau.com>'

BPH_NOTIFICATION_EMAIL = 'support@bhumipasahijau.com'

PASSWORD_RESET_TIMEOUT = 14400 # link aktif selama 4 jam (dalam detik)
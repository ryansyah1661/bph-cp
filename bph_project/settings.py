import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-gex9-d@0-b(8$h_d+o#ygfdlagtda09hv&d6t2-qt9l-m-@^wn'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'core', 
    'widget_tweaks',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'bph_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_bph',          # ← Nama database yang lu buat di Laragon tadi
        'USER': 'root',            # ← Default user Laragon itu root
        'PASSWORD': '',            # ← Default password Laragon itu kosong/blank
        'HOST': '127.0.0.1',       # ← Alamat lokal server
        'PORT': '3306',            # ← Port default MySQL
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================
# KONFIGURASI BAHASA DAN ZONA WAKTU SAKRAL (WIB)
# =============================================================
LANGUAGE_CODE = 'id'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True

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
# KONFIGURASI KEAMANAN SESSION LOGIN (KICK PAS BROWSER CLOSE)
# =============================================================
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Membatasi umur cookie aktif maksimal 1 jam (3600 detik) demi keamanan idle
SESSION_COOKIE_AGE = 3600
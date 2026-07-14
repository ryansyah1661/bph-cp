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

                'core.context_processors.unread_messages_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'bph_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_bph',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
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
# KONFIGURASI KEAMANAN SESSION LOGIN
# =============================================================
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600

# =============================================================
# 🚨 KONFIGURASI SURAT ELEKTRONIK (EMAIL SMTP) UNTUK RESET PASSWORD
# =============================================================

# 💡 PILIHAN 1: Pakai ini pas testing lokal (Isi email bakal dicetak langsung di terminal VS Code lu)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 💡 PILIHAN 2: Pakai ini kalau lu udah siap kirim email beneran lewat SMTP Gmail asli.
# (Jika ingin mengaktifkan Pilihan 2, hapus tanda '#' pada 7 baris di bawah dan beri '#' pada Pilihan 1)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'email_lu@gmail.com'  # ← Isi pakai alamat Gmail website/perusahaan
# EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'  # ← Isi pakai App Password 16 digit dari akun Google
# DEFAULT_FROM_EMAIL = 'Bhumi Pasa Hijau <email_lu@gmail.com>'
"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from django.utils.translation import gettext_lazy as _
from IPDD import jet_config
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-kbkkln+i3)+pmf7oaf8+v59+=7=ou%8u(65un%13xnt(-6!4b('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '5.59.233.207']

# Application definition
INSTALLED_APPS = [
    # Django-Jet
    'jet.dashboard',
    'jet',
    # Leaflet
    'leaflet',
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    # Constance
    'constance',
    'constance.backends.database',
    # Swagger docs
    'drf_yasg',
    # Celery
    'django_celery_beat',
    # Rest framework
    'rest_framework',
    'rest_framework.authtoken',
    # Localization
    'modeltranslation',
    # own apps
    'apps.post',
    'apps.core',
    'apps.category',
    'apps.authentication',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
X_FRAME_OPTIONS = 'ALLOWALL'

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'IPDD.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'IPDD.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'NAME': os.environ.get('DB_NAME', 'ipdd'),
        'USER': os.environ.get('DB_USER', 'ipdd'),
        'PASSWORD': os.environ.get('DB_PASS', 'ipdd'),
    },
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.contrib.gis.db.backends.postgis',
#         'HOST': os.environ.get('DB_HOST', '159.89.20.69'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#         'NAME': os.environ.get('DB_NAME', 'ipdd'),
#         'USER': os.environ.get('DB_USER', 'ipdd'),
#         'PASSWORD': os.environ.get('DB_PASS', 'ipdd'),
#     },
# }

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_USER_MODEL = 'authentication.Profile'

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Bishkek'

USE_I18N = True

# USE_TZ = False

MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]
LANGUAGES = (
    ('en', _('English')),
    ('ru', _('Russian')),
    ('ky', _('Kyrgyz')),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = 'staticfiles/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'utils.rest.CustomPageNumberPagination',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'utils.rest.CsrfExemptSessionAuthentication',
        'utils.rest.CustomTokenAuthentication',
    ],
    'PAGE_SIZE': 20,
}

# Redis configuration
CACHE_TTL = 600  # Seconds
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}',
        'KEY_PREFIX': 'ipdd',
        'TIMEOUT': CACHE_TTL,
    }
}

# Celery configuration
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_ENABLE_UTC = True

# Django-Jet settings
JET_SIDE_MENU_COMPACT = True
JET_SIDE_MENU_ITEMS = jet_config.menu_items
JET_THEMES = jet_config.themes
JET_INDEX_DASHBOARD = 'dashboard.dashboard.CustomIndexDashboard'
# JET_INDEX_DASHBOARD = 'jet.dashboard.dashboard.DefaultIndexDashboard'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# (42.87, 74.60) are the Bishkek city coordinates
LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (42.87, 74.60),
    'DEFAULT_ZOOM': 10,
    'RESET_VIEW': False,
    'TILES': [
        (
            'Carto Voyager',
            'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
            {'attribution': '&copy; <a href="https://carto.com/attributions">CARTO</a> &copy; OpenStreetMap'}
        ),
        (
            'OSM',
            'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            {'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}
        ),
        (
            'Carto',
            'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            {'attribution': '&copy; <a href="https://carto.com/attributions">CARTO</a> &copy; OpenStreetMap'}
        ),
    ],
}

from .constance_config import *

"""
Django settings for nm_portal project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from pathlib import Path

from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'DEV_KEY')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'DEV_JWT_KEY')
CERTIFICATE_TOKEN_KEY = os.environ.get(
    'CERTIFICATE_TOKEN_KEY', 'CERTIFICATE_TOKEN_KEY')

# SECURITY WARNING: don't run with debug turned o
DEBUG = True
###
ALLOWED_HOSTS = ['*']

LOCAL_TEST = True
DEV = True

#
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps
    'datarepo',
    'users',
    'college',
    'student',
    'lms',
    'reports',
    'skillofferings',
    'mmm',
    'psychometric',
    'kp',
    'fs',
    'simple',
    'industry_partners',
    'placements',
    'digi_locker',
    # packages
    'rest_framework',
    'rest_framework_simplejwt',
    'django_celery_beat',
    'django_celery_results',
    'corsheaders',
    'django_extensions',

]


CELERY_RESULT_BACKEND = "django-db"
CELERY_IMPORTS = ('users.task', 'college.registration.tasks')

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nm_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'nm_portal.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

#if DEV:
#    DATABASES = {
#        'default': {
#            'ENGINE': 'django.db.backends.sqlite3',
#            'NAME': BASE_DIR / 'db.sqlite3',
#        }
#    }
#else:
#    DATABASES = {
#        'default': {
#            'ENGINE': 'django.db.backends.postgresql_psycopg2',
#            'NAME': 'nmproject',
#            'USER': 'nm_user',
#            'PASSWORD': 'J35u5789!@#',
#            'HOST': '10.236.221.199',
#            'PORT': '5432',
#        }
#    }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'nm_portal',
#         'USER': 'postgres',
#         'PASSWORD': 'anil8096',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'nm_project',
#         'USER': 'postgres',
#         'PASSWORD': 'pgadmin',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'nmproject_may17',
        'USER': 'nm_user',
        'PASSWORD': 'J35u5789!@#',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "staticfiles"),)

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'rest_framework_xml.renderers.XMLRenderer',
    # )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': JWT_SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/media/admin/'

# # Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.tn.gov.in'
EMAIL_USE_TLS = True
EMAIL_PORT = 465
EMAIL_HOST_FROM = 'naanmudhalvan@tn.gov.in'

EMAIL_HOST_EMAIL = 'naanmudhalvan@tn.gov.in'
EMAIL_HOST_USER = ' naanmudhalvan'
EMAIL_HOST_USERNAME = ' naanmudhalvan'
EMAIL_RECEIVER_USER = 'naanmudhalvan@tn.gov.in'
EMAIL_HOST_PASSWORD = "*nmportal2922*"

# # Email
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'mail.tn.gov.in'
# EMAIL_USE_TLS = True
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'email.tnsdc'
# EMAIL_HOST_FROM = 'email.tnsdc@tn.gov.in'
# EMAIL_HOST_PASSWORD = 'eeHih5ta'


FRONT_END_URL = "http://portal.naanmudhalvan.tn.gov.in"
COLLEGE_FEE = 10000
CSRF_TRUSTED_ORIGINS = [
    'http://streaming.ldev.tech:2023',
    'https://streaming.ldev.tech:2023',
    'https://sandbox-api.naanmudhalvan.in',
    'http://sandbox-api.naanmudhalvan.in:3245',
    'https://sandbox-api.naanmudhalvan.in:3245',
    'https://api.naanmudhalvan.tn.gov.in',
    'https://localhost:8080',
    'https://localhost:3000',
    'http://localhost:8080',
    'http://localhost:3000',
    'https://ee11-117-247-183-95.in.ngrok.io'
]

CELERY_ALWAYS_EAGER = True

CORS_ORIGIN_ALLOW_ALL = True

# CORS_ORIGIN_WHITELIST = (
#     'http://localhost:8000',
#     'http://localhost:8080',
#     'http://localhost:8081',
# )

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

CUSTOM_SMTP_HOST = 'mail.tn.gov.in'
CUSTOM_SMTP_SENDER = 'naanmudhalvan@tn.gov.in'
CUSTOM_SMTP_USERNAME = 'naanmudhalvan'
CUSTOM_SMTP_PASSWORD = '*nmportal2922*'
"""



"""
MAX_UPLOAD_SIZE = "5242880"
# allow upload big file
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 50  # 50M
FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE

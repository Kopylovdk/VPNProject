"""
Django settings for vpnservice project.

Generated by 'django-admin startproject' using Django 2.2.28.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

import yaml

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

from log import logging_config_update

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(f'{BASE_DIR}/config.yaml', 'r', encoding='utf8') as stream:
    EXTERNAL_CFG = yaml.safe_load(stream)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = EXTERNAL_CFG['django']['secret_key']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = EXTERNAL_CFG['django']['debug']

ALLOWED_HOSTS = ['http://127.0.0.1:8080', 'http://localhost:8080', 'http://localhost:8000', '*']

LOGGING = logging_config_update(
    config=EXTERNAL_CFG['logging'],
    log_path=BASE_DIR)

DEMO_KEY_PERIOD = EXTERNAL_CFG['django']['demo_key_period']
DEMO_TRAFFIC_LIMIT = EXTERNAL_CFG['django']['demo_traffic_limit']
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.health_check',
    'apps.outline_vpn_admin',
    'apps.api',
    'django_apscheduler',
    'rest_framework',
    'rest_framework.authtoken',
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

ROOT_URLCONF = 'vpnservice.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'vpnservice.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': EXTERNAL_CFG['db']['name'],
        'USER': EXTERNAL_CFG['db']['user'],
        'PASSWORD': EXTERNAL_CFG['db']['password'],
        'HOST': EXTERNAL_CFG['db']['host'],
        'PORT': EXTERNAL_CFG['db']['port'],
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/


STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR + STATIC_URL

CSRF_TRUSTED_ORIGINS = ['http://localhost:8080', 'http://127.0.0.1:8080']

APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
APSCHEDULER_RUN_NOW_TIMEOUT = 25


REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'apps.api.exceptions.core_exception_handler',
    'NON_FIELD_ERRORS_KEY': 'error',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}

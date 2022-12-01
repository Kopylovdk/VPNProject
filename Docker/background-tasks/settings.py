import os
import yaml
from logs.config.logging_config_update import logging_config_update

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(f'{BASE_DIR}/config.yaml', 'r', encoding='utf8') as stream:
    EXTERNAL_CFG = yaml.safe_load(stream)

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = EXTERNAL_CFG['django']['debug']

with open(f'{BASE_DIR}/logs/config/log_config.yaml', 'r', encoding='utf8') as stream:
    EXTERNAL_LOG_CFG = yaml.safe_load(stream)

LOGGING = logging_config_update(
    config=EXTERNAL_LOG_CFG['logging'],
    log_path=BASE_DIR)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'apps.outline_vpn_admin',
    'django_apscheduler',
    'rest_framework.authtoken',
]

ROOT_URLCONF = 'vpnservice.urls'

WSGI_APPLICATION = 'vpnservice.wsgi.application'

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = False

APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
APSCHEDULER_RUN_NOW_TIMEOUT = 25

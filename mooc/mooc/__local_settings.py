# -*- coding: utf-8 -*-

# Local settings for mooc project.
LOCAL_SETTINGS = True
from settings import *

DEBUG = True

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.',
        # Or path to database file if using sqlite3.
        'NAME': '',
        # Not used with sqlite3.
        'USER': '',
        # Not used with sqlite3.
        'PASSWORD': '',
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': '',
        # Set to empty string for default. Not used with sqlite3.
        'PORT': '',
    }
}

# If you have Redis installed, copy this.
#CACHES = {
#    'default': {
#        'BACKEND': 'redis_cache.cache.RedisCache',
#        'LOCATION': '127.0.0.1:6379:5',
#        'OPTIONS': {
#            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
#        }
#    }
#}

# If you don't have Redis installed, copy this.
#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#        'LOCATION': 'mooc'
#    }
#}

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''
BADGE_SALT = ''
REGISTER_SALT = ''

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = ''
    EMAIL_PORT = ''
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    EMAIL_USE_TLS = True
    EMAIL_SUBJECT_PREFIX = ''
    
    

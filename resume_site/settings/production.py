"""
Production settings for resume_site.
"""
import os
from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    'resume.nonagonmedia.net',
    'localhost',
    '127.0.0.1',
    '.cluster.local',  # K8s internal DNS
    '*',  # Allow all for now (health checks use pod IP)
]

CSRF_TRUSTED_ORIGINS = [
    'https://resume.nonagonmedia.net',
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'resume_site'),
        'USER': os.environ.get('POSTGRES_USER', 'wagtail'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'wagtail'),
        'HOST': os.environ.get('POSTGRES_HOST', 'postgres'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# Security settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

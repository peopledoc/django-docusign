# -*- coding: utf-8 -*-
"""Django settings for django-docusign demo project."""
import os
from django.conf.global_settings import MIDDLEWARE_CLASSES


# Configure some relative directories.
demoproject_dir = os.path.dirname(os.path.abspath(__file__))
demo_dir = os.path.dirname(demoproject_dir)
root_dir = os.path.dirname(demo_dir)
data_dir = os.path.join(root_dir, 'var')
cfg_dir = os.path.join(root_dir, 'etc')


# Mandatory settings.
ROOT_URLCONF = 'django_docusign_demo.urls'
WSGI_APPLICATION = 'django_docusign_demo.wsgi.application'


# Database.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(data_dir, 'db.sqlite'),
    }
}


# Template.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]


# Required.
SECRET_KEY = "This is a secret made public on project's repository."

# Media and static files.
MEDIA_ROOT = os.path.join(data_dir, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(data_dir, 'static')
STATIC_URL = '/static/'

MIDDLEWARE_CLASSES += (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# Applications.
INSTALLED_APPS = (
    # The actual django-docusign demo.
    'django_docusign_demo',
    'django_docusign',
    'django_anysign',
    # Third-parties.
    'formsetfield',
    # Standard Django applications.
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Stuff that must be at the end.
    'django_nose',
)

USE_TZ = True

# BEGIN settings.ANYSIGN.
ANYSIGN = {
    'BACKENDS': {
        'docusign': 'django_docusign.backend.DocuSignBackend',
    },
    'SIGNATURE_TYPE_MODEL': 'django_docusign_demo.models.SignatureType',
    'SIGNATURE_MODEL': 'django_docusign_demo.models.Signature',
    'SIGNER_MODEL': 'django_docusign_demo.models.Signer',
}
# END settings.ANYSIGN.

# BEGIN settings.DOCUSIGN.
DOCUSIGN_ROOT_URL = 'https://demo.docusign.net/restapi/v2'
DOCUSIGN_TIMEOUT = 10
# END settings.DOCUSIGN.

# Test/development settings.
DEBUG = True
TEMPLATE_DEBUG = DEBUG
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
nose_cfg_dir = os.path.join(cfg_dir, 'nose')
NOSE_ARGS = [
    '--verbosity=2',
    '--no-path-adjustment',
    '--nocapture',
    '--all-modules',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django_dummysign': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django_anysign_demo': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

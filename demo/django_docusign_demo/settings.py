# -*- coding: utf-8 -*-
"""Django settings for django-docusign demo project."""
from os.path import abspath, dirname, join


# Configure some relative directories.
demoproject_dir = dirname(abspath(__file__))
demo_dir = dirname(demoproject_dir)
root_dir = dirname(demo_dir)
data_dir = join(root_dir, 'var')
cfg_dir = join(root_dir, 'etc')


# Mandatory settings.
ROOT_URLCONF = 'django_docusign_demo.urls'
WSGI_APPLICATION = 'django_docusign_demo.wsgi.application'


# Database.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(data_dir, 'db.sqlite'),
    }
}


# Required.
SECRET_KEY = "This is a secret made public on project's repository."

# Media and static files.
MEDIA_ROOT = join(data_dir, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = join(data_dir, 'static')
STATIC_URL = '/static/'


# Applications.
INSTALLED_APPS = (
    # The actual django-docusign demo.
    'django_docusign_demo',
    # Third-parties.
    'south',
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


# Test/development settings.
DEBUG = True
TEMPLATE_DEBUG = DEBUG
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
nose_cfg_dir = join(cfg_dir, 'nose')
NOSE_ARGS = [
    '--verbosity=2',
    '--no-path-adjustment',
    '--nocapture',
    '--all-modules',
    '--rednose',
]
SOUTH_TESTS_MIGRATE = False


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
            'class': 'django.utils.log.NullHandler',
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
        'django_dummysign': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

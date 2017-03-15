import os
import sys

import dj_database_url

if "DATABASE_URL" not in os.environ or \
        not os.environ["DATABASE_URL"].startswith("postgres://"):
    print("\n".join(
        l.strip() for l in
        """It seems you have not configured the path to your PGSQL database.
        To do so, use the DATABASE_URL environment variable like this :

        DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME

        (where all optional parts can be omited to get their default value)
        """.splitlines()))
    sys.exit(1)

DEBUG = True
USE_TZ = True
DATABASES = {"default": dj_database_url.config()}
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django_north",
    "tests.north_app",
]
STATIC_URL = "/static/"
SITE_ID = 1
MIDDLEWARE_CLASSES = ()
LOGGING = {}
SECRET_KEY = "yay"

NORTH_MANAGE_DB = True
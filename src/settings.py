# Initialize App Engine and import the default settings (DB backend, etc.).
# If you want to use a different backend you have to remove all occurences
# of "djangoappengine" from this file.
from djangoappengine.settings_base import *

import os
import mimetypes
import logging

# Activate django-dbindexer for the default database
DATABASES['native'] = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}
AUTOLOAD_SITECONF = 'indexes'

SECRET_KEY = '=r-$b*8hglm+858&9t043hlm6-&6-3d3vfc4((7yd0dbrakhvi'

DEBUG=True

APP_NAME = 'spuds.com'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'djangotoolbox',
    'autoload',
    'dbindexer',
    'registration',

    # djangoappengine should come last, so it can override a few manage.py commands
    'djangoappengine',
    'website.home'
)

MIDDLEWARE_CLASSES = (
    # This loads the index definitions, so it has to come first
    'autoload.middleware.AutoloadMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
)

# This test runner captures stdout and associates tracebacks with their
# corresponding output. Helps a lot with print-debugging.
TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'

ADMIN_MEDIA_PREFIX = '/media/admin/'
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'website/templates'),)

ROOT_URLCONF = 'urls'

EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_BACKEND = 'appengine_emailbackend.EmailBackend'
EMAIL_BACKEND = 'djangoappengine.mail.EmailBackend'

mimetypes.add_type("application/vnd.ms-fontobject", ".eot")
mimetypes.add_type("application/x-font-ttf", ".ttc")
mimetypes.add_type("application/x-font-ttf", ".ttf")
mimetypes.add_type("font/opentype", ".otf")
mimetypes.add_type("application/x-font-woff", ".woff")

LOGIN_REDIRECT_URL = '/'
ACCOUNT_ACTIVATION_DAYS = 5
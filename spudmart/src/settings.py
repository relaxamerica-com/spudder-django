import os
import mimetypes
from djangoappengine.settings_base import *
from spudmart.utils.app_identity import get_application_version

# Activate django-dbindexer for the default database

DATABASES['native'] = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native', 'HIGH_REPLICATION' : True}
AUTOLOAD_SITECONF = 'indexes'

DEBUG=True

APP_NAME = 'Spudmart'

AUTH_PROFILE_MODULE = 'accounts.UserProfile'

AWS_ACCESS_KEY_ID = 'AKIAIEUN2XKQF4ZU7UDA'
AWS_SECRET_KEY_ID = 'CIwpNtDm6OBGUiOGxjZ+XqdOjMPhhaFgTi7c1Ah/'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'djangotoolbox',
    'autoload',
    'dbindexer',
    'boto',
    'spudmart.utils',
    'spudmart.home',
    'spudmart.accounts',
    'spudmart.donations',
    'spudmart.recipients',
    'spudmart.dashboard',
    'djangoappengine'
)

MIDDLEWARE_CLASSES = (
    # This loads the index definitions, so it has to come first
    'autoload.middleware.AutoloadMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'spudmart.accounts.middleware.SponsorMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'spudmart.amazon.context.amazon_client_id'
)

# This test runner captures stdout and associates tracebacks with their
# corresponding output. Helps a lot with print-debugging.
TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'

ADMIN_MEDIA_PREFIX = '/media/admin/'
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)

ROOT_URLCONF = 'urls'

DEFAULT_FROM_EMAIL = 'lukasz@spudder.com'
EMAIL_BACKEND = 'djangoappengine.mail.EmailBackend'

# For the development purposes
#EMAIL_HOST = 'localhost'
#EMAIL_PORT = 1025
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_BACKEND = 'appengine_emailbackend.EmailBackend'

mimetypes.add_type("application/vnd.ms-fontobject", ".eot")
mimetypes.add_type("application/x-font-ttf", ".ttc")
mimetypes.add_type("application/x-font-ttf", ".ttf")
mimetypes.add_type("font/opentype", ".otf")
mimetypes.add_type("application/x-font-woff", ".woff")

LOGIN_REDIRECT_URL = '/'
ACCOUNT_ACTIVATION_DAYS = 5

# Make this unique, and don't share it with anybody.
SECRET_KEY = '8lu*6g0lg)9z!ba+a$ehk)xt)x%rxgb$i1&amp;022shmi1jcgihb*'

app_version = get_application_version()
# app_version = 'spudmart'

spudmart_settings = {
    'spudder_application_id': 'RwjN7ubrqVZSXcwd2AWaQtov6Mgsi7hAXZ510xTR',
    'spudder_rest_api_key': 'aY5jEVPGJadgWcd2gOecgnzMNKDS9Igx8d5DNU04',
    'spudder_base_url': 'https://spudmart.parseapp.com',
    'spudmart_base_url': 'https://spudmart-dot-spudmart1.appspot.com',
    'amazon_login_client_id': 'amzn1.application-oa2-client.f46864c6f8bb40d1bc2c3d211c514486'
}

lukasz_settings = {
    'spudder_application_id': 'QZjpmUJQEwBE6Wc0YfKEMRwv2C5Aeb4qQbopyIg9',
    'spudder_rest_api_key': 'S47GCWTSehKpwwJ2y8iXVnoYLWqOoPyydKiyWYYb',
    'spudder_base_url': 'https://spudmartlukasz.parseapp.com',
    'spudmart_base_url': 'https://lukasz-dot-spudmart1.appspot.com',
    'amazon_login_client_id': 'amzn1.application-oa2-client.de78cbafe055444aa00e07a445644d16'
}

karol_settings = {
    'spudder_application_id': 'YU4g6sCW8Dvl6khJsVYgXhr20Pu5zaaLcIQ4oRON',
    'spudder_rest_api_key': 'AbvJ682IvzXdWMMi1CbdONZHZhdJH4gFEyTWo4k9',
    'spudder_base_url': 'https://karol.parseapp.com',
    'spudmart_base_url': 'https://karol-dot-spudmart1.appspot.com',
    'amazon_login_client_id': 'amzn1.application-oa2-client.d8fccc9c77624577898dca9ff517eff3'
}

shared_settings = {
    'spudmart': spudmart_settings,
    'paymentsspudmart': spudmart_settings,  # backend
    'lukasz': lukasz_settings,
    'paymentslukasz': lukasz_settings,  # backend
    'karol': karol_settings,
    'paymentskarol': karol_settings  # backend
}

SPUDDER_APPLICATION_ID = shared_settings[app_version]['spudder_application_id']
SPUDDER_REST_API_KEY = shared_settings[app_version]['spudder_rest_api_key']
SPUDDER_BASE_URL = shared_settings[app_version]['spudder_base_url']
SPUDMART_BASE_URL = shared_settings[app_version]['spudmart_base_url']
AMAZON_LOGIN_CLIENT_ID = shared_settings[app_version]['amazon_login_client_id']


GOOGLE_PLACES_API_KEY = 'AIzaSyBY2lT_31eUX7yTH90gyPXxcJvM4pqSycs'
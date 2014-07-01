import os
import mimetypes
import socket
from djangoappengine.settings_base import *
from spudmart.utils.app_identity import get_spudmart_app_name

# Activate django-dbindexer for the default database

DATABASES['native'] = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native', 'HIGH_REPLICATION' : True}
AUTOLOAD_SITECONF = 'indexes'

DEBUG = True
if socket.gethostname() == 'www.spudder.com':
    DEBUG = False
else:
    DEBUG = True

APP_NAME = 'Spudmart'

AUTH_PROFILE_MODULE = 'accounts.UserProfile'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'djangotoolbox',
    'djangoappengine',
    'django_nose',
    'autoload',
    'dbindexer',
    'boto',
    'bootstrap3',  # Bootstrap3 provides bootstrap 3 style form rendering
    'spudmart.utils',
    'spudmart.home',
    'spudmart.accounts',
    'spudmart.donations',
    'spudmart.recipients',
    'spudmart.dashboard',
    'spudmart.venues',
    'spudmart.upload',
    'spudmart.sponsors',
    'spudmart.hospitals',
    'spudmart.api',
    'spudmart.CERN',
    'spudmart.amazon',
    'spudmart.utils',
    'spudderadmin',
    'spudderaccounts',
    'spudderdomain',
)

MIDDLEWARE_CLASSES = (
    # This loads the index definitions, so it has to come first
    'autoload.middleware.AutoloadMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'spudmart.accounts.middleware.SponsorMiddleware',
    'spuddermiddleware.SSL_Middleware.SSLRedirect',
    'spuddermiddleware.staffmiddleware.StaffMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'spudmart.amazon.context.amazon_client_id',
    'spuddercontextprocessors.appenginhelpers.context_running_locally',
    'spuddercontextprocessors.staffcontext.staff_context',
    'spuddercontextprocessors.settingscontext.settings_context',
)


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

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--with-xunit', '--xunit-file=spudmart/test-reports/xunit.xml', '-v']
NOSE_PLUGINS = ['nose_plugins.noseplugins.TestDiscoveryPlugin']

# Make this unique, and don't share it with anybody.
SECRET_KEY = '8lu*6g0lg)9z!ba+a$ehk)xt)x%rxgb$i1&amp;022shmi1jcgihb*'

app_name = get_spudmart_app_name()

shared_settings = {
    'spudmart1': {  # main testing environment
        'server_email': 'help@spuder.com',
        'spudder_application_id': 'RwjN7ubrqVZSXcwd2AWaQtov6Mgsi7hAXZ510xTR',
        'spudder_rest_api_key': 'aY5jEVPGJadgWcd2gOecgnzMNKDS9Igx8d5DNU04',
        'spudder_base_url': 'https://spudmart.parseapp.com',
        'spudmart_base_url': 'https://spudmart1.appspot.com',
        'amazon_login_client_id': 'amzn1.application-oa2-client.4637978bf71a44fdb057225c55e78d12',
        'linkedin_api_key': '77rm3ugcrdkqk7',
        'linkedin_secret_key': '7BlAnjhz5FetO09O',

    },
    'sharp-avatar-587': {  # lukasz@spuder.com
        'server_email': 'lukasz@spuder.com',
        'spudder_application_id': 'QZjpmUJQEwBE6Wc0YfKEMRwv2C5Aeb4qQbopyIg9',
        'spudder_rest_api_key': 'S47GCWTSehKpwwJ2y8iXVnoYLWqOoPyydKiyWYYb',
        'spudder_base_url': 'https://spudmartlukasz.parseapp.com',
        'spudmart_base_url': 'https://sharp-avatar-587.appspot.com',
        'amazon_login_client_id': 'amzn1.application-oa2-client.de78cbafe055444aa00e07a445644d16',
        'linkedin_api_key': '',
        'linkedin_secret_key': '',

    },
    'essential-hawk-597': {  # karol@spudder.com
        'server_email': 'karol@spuder.com',
        'spudder_application_id': 'YU4g6sCW8Dvl6khJsVYgXhr20Pu5zaaLcIQ4oRON',
        'spudder_rest_api_key': 'AbvJ682IvzXdWMMi1CbdONZHZhdJH4gFEyTWo4k9',
        'spudder_base_url': 'https://spudmartkarol.parseapp.com',
        'spudmart_base_url': 'https://essential-hawk-597.appspot.com',
        'amazon_login_client_id': 'amzn1.application-oa2-client.d8fccc9c77624577898dca9ff517eff3',
        'linkedin_api_key': '',
        'linkedin_secret_key': '',

    },
    'ahmed': {
        'server_email': 'help@spuder.com',
        'spudder_application_id': '',
        'spudder_rest_api_key': '',
        'spudder_base_url': 'https://karol.parseapp.com',
        'spudmart_base_url': 'https://ahmed-dot-spudmart1.appspot.com',
        'amazon_login_client_id': 'amzn1.application-oa2-client.d8fccc9c77624577898dca9ff517eff3',
        'linkedin_api_key': '',
        'linkedin_secret_key': '',

    },
    'genial-union-587': {  # lucy@spudder.com
        'server_email': 'lucy@spuder.com',
        'spudder_application_id': '',
        'spudder_rest_api_key': '',
        'spudder_base_url': 'https://spudmart.parseapp.com',
        'spudmart_base_url': 'https://genial-union-587.appspot.com',
        'amazon_login_client_id': 'amzn1.application-oa2-client.b1404a35a0484c64a0fdf150a8a7a6f2',
        'linkedin_api_key': '77rqz7l270vhsb',
        'linkedin_secret_key': '5PcKrcRI2m5q4zWP',
    },
    'spudmartmatt': {  # mg@metalayer.com
        'server_email': 'mg@metalayer.com',
        'spudder_application_id': '',
        'spudder_rest_api_key': '',
        'spudder_base_url': 'https://spudmart.parseapp.com',
        'spudmart_base_url': 'https://spudmartmatt.appspot.com',
        'amazon_login_client_id': 'amzn1.application-oa2-client.ee0b298ab0ce4be99ef0527da3c4820a',
        'linkedin_api_key': '',
        'linkedin_secret_key': '',

    },
    'spudder-live': {  #mg@metalayer.com
        'server_email': 'help@spuder.com',
        'spudder_application_id': '',
        'spudder_rest_api_key': '',
        'spudder_base_url': 'https://spudmart.parseapp.com',
        'spudmart_base_url': 'https://spudder-live.appspot.com',
        'amazon_login_client_id': 'amzn1.application-oa2-client.47892dcda29f4d3d8c437b7c44f1b6e6',
        'linkedin_api_key': '77acg7pe6xdqfo',
        'linkedin_secret_key': 'Eh1uPylFg3RMSOu9',

    },
    'livespudder': {  #mg@metalayer.com
        'server_email': 'help@spuder.com',
        'spudder_application_id': '',
        'spudder_rest_api_key': '',
        'spudder_base_url': 'https://spudmart.parseapp.com',
        'spudmart_base_url': 'https://livespudder.appspot.com',
        'amazon_login_client_id': 'amzn1.application-oa2-client.47892dcda29f4d3d8c437b7c44f1b6e6',
        'linkedin_api_key': '77acg7pe6xdqfo',
        'linkedin_secret_key': 'Eh1uPylFg3RMSOu9',

    },
}

SPUDDER_APPLICATION_ID = shared_settings[app_name]['spudder_application_id']
SPUDDER_REST_API_KEY = shared_settings[app_name]['spudder_rest_api_key']
SPUDDER_BASE_URL = shared_settings[app_name]['spudder_base_url']
SPUDMART_BASE_URL = shared_settings[app_name]['spudmart_base_url']
AMAZON_LOGIN_CLIENT_ID = shared_settings[app_name]['amazon_login_client_id']
SERVER_EMAIL = shared_settings[app_name]['server_email']
LINKEDIN_API_KEY = shared_settings[app_name]['linkedin_api_key']
LINKEDIN_SECRET_KEY = shared_settings[app_name]['linkedin_secret_key']

# Configuration shared across all applications
AWS_ACCESS_KEY_ID = 'AKIAIEUN2XKQF4ZU7UDA'
AWS_SECRET_KEY_ID = 'CIwpNtDm6OBGUiOGxjZ+XqdOjMPhhaFgTi7c1Ah/'
GOOGLE_PLACES_API_KEY = 'AIzaSyBY2lT_31eUX7yTH90gyPXxcJvM4pqSycs'

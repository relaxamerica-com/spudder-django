import os
import mimetypes
import socket
from djangoappengine.settings_base import *
from spudmart.utils.app_identity import get_spudmart_app_name

# Activate django-dbindexer for the default database

DATABASES['native'] = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native', 'HIGH_REPLICATION' : True}
AUTOLOAD_SITECONF = 'indexes'


class Environments:
    LIVE = 'live'
    STAGE = 'stage'
    DEV = 'dev'

ENVIRONMENT = Environments.DEV

DEBUG = True

if socket.gethostname() == 'www.spudder.com':
    ENVIRONMENT = Environments.LIVE
    DEBUG = False
elif 'spudmart1' in socket.gethostname():
    ENVIRONMENT = Environments.STAGE
else:
    DEBUG = True

APP_NAME = 'Spudmart'

AUTH_PROFILE_MODULE = 'accounts.UserProfile'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
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
    'spudmart.flags',
    'spudderadmin',
    'spudderaccounts',
    'spudderdomain',
    'spudderkrowdio',
    'spuddersocialengine',
    'spudderspuds',
)

MIDDLEWARE_CLASSES = (
    # This loads the index definitions, so it has to come first
    'autoload.middleware.AutoloadMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'spudmart.accounts.middleware.SponsorMiddleware',
    'spuddermiddleware.SSL_Middleware.SSLRedirect',
    'spuddermiddleware.spuddersharedsettingsmiddleware.EnsureSharedSettingsMiddleware',
    'spuddermiddleware.staffmiddleware.StaffMiddleware',
    'spuddermiddleware.spudderaccountsmiddleware.RolesMiddleware',
    'spuddermiddleware.spudderaccountsmiddleware.AccountPasswordMiddleware',
    'spuddermiddleware.spudderaccountsmiddleware.EditPageMiddleware',
    'spuddermiddleware.spudderaccountsmiddleware.FollowMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'spuddercontextprocessors.spudderaccountscontext.current_role_context',
    'spuddercontextprocessors.spudderaccountscontext.other_roles_context',
    'spuddercontextprocessors.spudderaccountscontext.amazon_client_id',
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

SPORTS = [
    'Baseball', 'Basketball', 'Field Hockey', 'Football',
    'Ice Hockey', 'Lacrosse', 'Rugby', 'Soccer', 'Softball',
    'Swimming', 'Tennis', 'Track and Field', 'Volleyball',
    'Waterpolo', 'Wrestling']

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
        'instagram_client_id': '3888eac365f7468dabd5bf9ad06c8930',
        'instagram_client_secret': 'b1bc01bf1a9944e2834288484f450ab2',
        'twitter_client_secret': 'lVgYuiP2QBKl0vOOX3swt9ynQheP3zQMUBN6Jcm3I',
        'twitter_client_id': 'OSwUJxPN7xkwEpVufgp0w',
        'twitter_access_token': '481249312-aFVuYa0HUCTKV7bc3Xrnk2twNHXwLV6r3uteKwe0',
        'twitter_access_token_secret': 'hHPebsFws3AcWyDrAvjnxapUJ95JI15NjZ7TwiXgF5f3v',
        'support_email': 'support@spudder.com',
        'krowdio_client_key': '53fc72a6f1f70e3fc79f0876',

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
        'support_email': 'lukasz@spuder.com',
        'krowdio_client_key': '5401e324e9b6cc56dbe43f55'

    },
    'essential-hawk-597': {  # karol@spuder.com
        'server_email': 'karol@spuder.com',
        'spudder_application_id': 'YU4g6sCW8Dvl6khJsVYgXhr20Pu5zaaLcIQ4oRON',
        'spudder_rest_api_key': 'AbvJ682IvzXdWMMi1CbdONZHZhdJH4gFEyTWo4k9',
        'spudder_base_url': 'https://spudmartkarol.parseapp.com',
        'spudmart_base_url': 'https://essential-hawk-597.appspot.com',
        'amazon_login_client_id': 'amzn1.application-oa2-client.d8fccc9c77624577898dca9ff517eff3',
        'linkedin_api_key': '',
        'linkedin_secret_key': '',
        'support_email': 'karol@spuder.com',

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
        'support_email': '',

    },
    'genial-union-587': {  # lucy@spuder.com
        'server_email': 'lucy@spuder.com',
        'spudder_application_id': '',
        'spudder_rest_api_key': '',
        'spudder_base_url': 'https://spudmart.parseapp.com',
        'spudmart_base_url': 'https://genial-union-587.appspot.com',
        'amazon_login_client_id': 'amzn1.application-oa2-client.b1404a35a0484c64a0fdf150a8a7a6f2',
        'linkedin_api_key': '77rqz7l270vhsb',
        'linkedin_secret_key': '5PcKrcRI2m5q4zWP',
        'support_email': 'lucy@spuder.com',
        'instagram_client_id': '6faaf69fe18846a79e8c4b6805d3fc6f',
        'instagram_client_secret': 'fe7144dacd244102a12a75713b0de7e6',
        'twitter_client_secret': 'DOyZkpOBVlmF4hyusZDyEhZqtM2FYvLWkhu7560tCIqCeUANmI',
        'twitter_client_id': 'eNsFMF33Gs0p6P0KIWj0WizvW',
        'twitter_access_token': '2573288766-Z27sWN4Hi812Nqt0yQ4foKTVr4njfXX2DeP4MTa',
        'twitter_access_token_secret': 'aIRQheX0medxdnXLG2MXfebNB78ftRFf97pe8hUvHtr75',
        'krowdio_client_key': '53ff5196f1f70e3fc79f136c',
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
        'instagram_client_id': '3888eac365f7468dabd5bf9ad06c8930',
        'instagram_client_secret': 'b1bc01bf1a9944e2834288484f450ab2',
        'support_email': 'mg@metalayer.com',
        'krowdio_client_key': '53ff5196f1f70e3fc79f136c',

    },
    'livespudder': {  #mg@metalayer.com
        'server_email': 'help@spuder.com',
        'spudder_application_id': '',
        'spudder_rest_api_key': '',
        'spudder_base_url': 'https://spudmart.parseapp.com',
        'spudmart_base_url': 'https://www.spudder.com',
        'amazon_login_client_id': 'amzn1.application-oa2-client.47892dcda29f4d3d8c437b7c44f1b6e6',
        'linkedin_api_key': '77acg7pe6xdqfo',
        'linkedin_secret_key': 'Eh1uPylFg3RMSOu9',
        'instagram_client_id': '3888eac365f7468dabd5bf9ad06c8930',
        'instagram_client_secret': 'b1bc01bf1a9944e2834288484f450ab2',
        'twitter_client_secret': '',
        'twitter_client_id': '',
        'twitter_access_token': '',
        'twitter_access_token_secret': '',
        'support_email': 'support@spudder.com',
        'krowdio_client_key': '52769e9ff1f70e0552df58a4',
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
INSTAGRAM_CLIENT_ID = shared_settings[app_name].get('instagram_client_id', '')
INSTAGRAM_CLIENT_SECRET = shared_settings[app_name].get('instagram_client_secret', '')
TWITTER_CLIENT_SECRET = shared_settings[app_name].get('twitter_client_secret', '')
TWITTER_CLIENT_ID = shared_settings[app_name].get('twitter_client_id', '')
TWITTER_ACCESS_TOKEN = shared_settings[app_name].get('twitter_access_token', '')
TWITTER_ACCESS_TOKEN_SECRET = shared_settings[app_name].get('twitter_access_token_secret', '')
SUPPORT_EMAIL = shared_settings[app_name]['support_email']
KROWDIO_CLIENT_KEY = shared_settings[app_name].get('krowdio_client_key', None)
AT_POST_SPUD_BASE_TWEET_ID = 503359742325321728


# Configuration shared across all applications
AWS_ACCESS_KEY_ID = 'AKIAIEUN2XKQF4ZU7UDA'
AWS_SECRET_KEY_ID = 'CIwpNtDm6OBGUiOGxjZ+XqdOjMPhhaFgTi7c1Ah/'
GOOGLE_PLACES_API_KEY = 'AIzaSyBY2lT_31eUX7yTH90gyPXxcJvM4pqSycs'
KROWDIO_GLOBAL_PASSWORD = 'spudtastic'

LOGIN_URL = '/users/account/signin'

from features import *
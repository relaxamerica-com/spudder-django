from django.conf.urls.defaults import *
from spudmart.utils.url import determine_ssl

urlpatterns = patterns('spudderclubs.views',
    (r'^$', 'splash'),

    (r'register$', 'register', {'SSL': determine_ssl()}),
    (r'register/recipient$', 'register_as_recipient', {'SSL': determine_ssl()}),
    (r'register/recipient/complete$', 'register_as_recipient_complete'),
    (r'register/recipient/error$', 'register_as_recipient_error'),
    (r'register/recipient/verification_pending$', 'register_as_recipient_pending_verification'),
    (r'register/profile', 'register_profile_info'),

    (r'^signin$', 'signin', {'SSL': determine_ssl()}),

    (r'^dashboard$', 'dashboard'),
    (r'^profile$', 'profile'),
)


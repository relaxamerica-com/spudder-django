from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderspuds.views',

    url(r'signin$', 'user_signin'),
    url(r'register$', 'user_register'),
    url(r'register_add_fan_role/complete$', 'user_add_fan_role_complete'),
    url(r'register_add_fan_role$', 'user_add_fan_role'),
    url(r'', 'landing_page'),
)



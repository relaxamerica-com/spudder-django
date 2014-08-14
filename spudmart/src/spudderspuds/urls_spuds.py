from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderspuds.views',

    # /spuds/ urls
    url(r'signin$', 'fan_signin'),
    url(r'register$', 'fan_register'),
    url(r'register_add_fan_role$', 'user_add_fan_role'),

    url(r'', 'landing_page'),
)



from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderspuds.views',

    url(r'signin$', 'user_signin'),
    url(r'register$', 'user_register'),
    url(r'', 'landing_page'),
)



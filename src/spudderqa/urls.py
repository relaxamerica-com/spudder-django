from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderqa.views',

    url(r'signin', 'signin'),
    url(r'', 'dashboard'),
)

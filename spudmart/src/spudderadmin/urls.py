from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderadmin.views',

    url('^/dashboard', 'admin_dashboard'),
    url('^/cern', 'cern_dashboard'),
    url('^', 'admin_login'),
)
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderadmin.views',

    url('^/dashboard', 'admin_dashboard', name='admin_dashboard'),
    url('^', 'admin_login', name='admin_login'),
)
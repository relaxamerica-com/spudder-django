from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderaffiliates.views',

    url('^/dashboard$', 'affiliate_dashboard'),

    url(r'^', 'affiliate_login'),
)
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderaccounts.views',

    url('^$', 'accounts_dashboard',),
    url('^/signin', 'accounts_signin',),
)
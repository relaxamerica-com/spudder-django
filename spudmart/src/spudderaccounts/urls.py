from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderaccounts.views',

    url('^$', 'accounts_dashboard',),
    url('^/signin', 'accounts_signin',),

    url('^/roles/student/(?P<entity_id>\d+)', 'accounts_manage_role',),
)
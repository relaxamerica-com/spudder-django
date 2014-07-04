from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderaccounts.views',

    url('signin', 'accounts_signin',),

    url('roles/add', 'accounts_add_role'),
    url('roles/create/(?P<entity_type>\w+)', 'accounts_create_role'),
    url('roles/manage/(?P<entity_type>\w+)/(?P<entity_id>\d+)', 'accounts_manage_role'),
    url('roles/delete/(?P<entity_type>\w+)/(?P<entity_id>\d+)', 'accounts_delete_role'),
    url('roles/activate/(?P<entity_type>\w+)/(?P<entity_id>\d+)', 'accounts_activate_role'),

    url('$', 'accounts_dashboard',),
)
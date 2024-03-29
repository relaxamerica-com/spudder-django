import os
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderaccounts.views',


    url('roles/add', 'accounts_add_role'),
    url('roles/create/(?P<entity_type>\w+)', 'accounts_create_role'),
    url('roles/manage/(?P<entity_type>\w+)/(?P<entity_id>\d+)', 'accounts_manage_role'),
    url('roles/delete/(?P<entity_type>\w+)/(?P<entity_id>\d+)', 'accounts_delete_role'),
    url('roles/activate/(?P<entity_type>\w+)/(?P<entity_id>\d+)', 'accounts_activate_role'),

    url('invitation/(?P<invitation_id>\d+)$', 'accept_invitation'),
    url('invitation/(?P<invitation_id>\d+)/cancel$', 'cancel_invitation'),

    url('account/create_password', 'accounts_create_password'),
    url('account/signin/(?P<user_id>\d+)', 'accounts_signin',),
    url('account/signin', 'accounts_signin_choose_account', {'SSL' : True }),
    url('account/forgot', 'account_forgot_password'),
    url('account/reset_password', 'account_reset_password'),
    url('$', 'accounts_dashboard',),
)
from django.conf.urls.defaults import *
from spudderdomain.controllers import RoleController

urlpatterns = patterns(
    'spudderaccounts.views',

    url('signin', 'accounts_signin',),

    url('roles/student/(?P<entity_id>\d+)', 'accounts_manage_role',
        {'role_type': RoleController.ENTITY_STUDENT}),

    url('$', 'accounts_dashboard',),
)
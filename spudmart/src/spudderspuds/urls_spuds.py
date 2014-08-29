from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderspuds.views',

    # /spuds/ urls
    url(r'signin$', 'fan_signin'),
    url(r'register$', 'fan_register'),
    url(r'register_add_fan_role$', 'user_add_fan_role'),
    url(r'search/teams', 'entity_search', {'entity_type': 'team'}),
    url(r'search/fans', 'entity_search', {'entity_type': 'fan'}),


    # /s/ urls - unclaimed atpostspuds
    (r'^(?P<spud_id>\d+)$', 'claim_atpostspud'),

    (r'^at_names', 'get_at_names'),

    url(r'', 'landing_page'),
)



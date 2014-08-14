from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderspuds.views',

    # /spuds/ urls
    url(r'signin$', 'fan_signin'),
    url(r'register$', 'fan_register'),
    url(r'register_add_fan_role$', 'user_add_fan_role'),

    # /fan/ urls
    (r'^(?P<page_id>\d+)$', 'fan_profile_view'),
    (r'^(?P<page_id>\d+)/edit$', 'fan_profile_edit'),
    (r'^(?P<page_id>\d+)/edit_cover$', 'fan_profile_edit_cover'),
    (r'^(?P<page_id>\d+)/save_cover$', 'fan_profile_save_cover'),
    (r'^(?P<page_id>\d+)/reset_cover$', 'fan_profile_reset_cover'),
    (r'^(?P<page_id>\d+)/save_avatar$', 'fan_profile_save_avatar'),
    (r'^(?P<page_id>\d+)/teams$', 'fan_my_teams'),


    url(r'', 'landing_page'),
)



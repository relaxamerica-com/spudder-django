from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderspuds.views',

    (r'^(?P<page_id>\d+)$', 'fan_profile_view'),
    (r'^(?P<page_id>\d+)/edit$', 'fan_profile_edit'),
    (r'^(?P<page_id>\d+)/edit_cover$', 'fan_profile_edit_cover'),
    (r'^(?P<page_id>\d+)/save_cover$', 'fan_profile_save_cover'),
    (r'^(?P<page_id>\d+)/reset_cover$', 'fan_profile_reset_cover'),
    (r'^(?P<page_id>\d+)/save_avatar$', 'fan_profile_save_avatar'),
    (r'^(?P<page_id>\d+)/teams$', 'fan_my_teams'),
    (r'^disable_about/$', 'disable_about'),
    (r'^start_following$', 'start_following_view'),
    (r'^stop_following$', 'stop_following_view'),
    (r'^follow$', 'follow'),
    (r'^test$', 'test_spuds'),
    (r'^add_spud_comment', 'add_spud_comment'),
    url(r'', 'landing_page'),
)



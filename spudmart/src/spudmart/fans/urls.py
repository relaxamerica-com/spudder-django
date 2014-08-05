from django.conf.urls.defaults import patterns


urlpatterns = patterns(
    'spudmart.fans.views',
    (r'^$', 'fan_dashboard'),
    (r'^page$', 'fan_page'),
    (r'^(?P<page_id>\d+)$', 'public_view'),
    (r'^(?P<page_id>\d+)/save_social_media$', 'save_social_media'),
    (r'^(?P<page_id>\d+)/save_cover$', 'save_cover'),
    (r'^(?P<page_id>\d+)/reset_cover$', 'reset_cover'),
    (r'^(?P<page_id>\d+)/save_avatar$', 'save_avatar'),
    (r'^remove_avatar$', 'remove_avatar'),
)
from django.conf.urls.defaults import patterns


urlpatterns = patterns(
    'spudmart.fans.views',
    (r'^$', 'fan_dashboard'),
    (r'^page$', 'fan_page'),
    (r'^(?P<page_id>\d+)$', 'public_view'),
    (r'^remove_avatar$', 'remove_avatar'),
)
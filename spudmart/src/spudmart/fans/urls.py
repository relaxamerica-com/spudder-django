from django.conf.urls.defaults import patterns


urlpatterns = patterns(
    'spudmart.fans.views',
    (r'^dashboard$', 'fan_dashboard'),
    (r'^page$', 'fan_page'),
    (r'^(?P<page_id>\d*)$', 'view'),
    (r'^(?P<page_id>\d+)/edit_cover$', 'edit_cover'),
    (r'^(?P<page_id>\d+)/save_cover$', 'save_cover'),
    (r'^(?P<page_id>\d+)/reset_cover$', 'reset_cover'),
    (r'^(?P<page_id>\d+)/save_avatar$', 'save_avatar'),
)
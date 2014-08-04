from django.conf.urls.defaults import patterns


urlpatterns = patterns(
    'spudmart.sponsors.views',
    (r'^page$', 'sponsor_page'),
    (r'^(?P<page_id>\d+)$', 'public_view'),
    (r'^venues/$', 'sponsors_venues'),
    (r^'helloci', 'helloci'),
    (r'^$', 'sponsors_dashboard'),
)
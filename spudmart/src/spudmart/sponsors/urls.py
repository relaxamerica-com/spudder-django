from django.conf.urls.defaults import patterns


urlpatterns = patterns(
    'spudmart.sponsors.views',
    (r'^page$', 'sponsor_page'),
    (r'^venues/$', 'sponsors_venues'),
    (r'^$', 'sponsors_dashboard'),
)
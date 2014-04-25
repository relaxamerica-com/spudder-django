from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.venues.views',
    (r'^view/(?P<venue_id>\d+)$', 'view'),
    (r'^create$', 'create'),
)
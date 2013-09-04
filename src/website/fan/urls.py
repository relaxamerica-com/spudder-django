from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('website.fan.views',
    (r'^spuds$', 'spuds'),
    (r'^fans$', 'fans'),
    (r'^public/(?P<user_id>\d+)$', 'public_view'),
)

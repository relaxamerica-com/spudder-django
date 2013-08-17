from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('website.fan.views',
    (r'^$', 'spuds'),
)

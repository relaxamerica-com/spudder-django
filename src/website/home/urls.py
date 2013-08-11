from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('website.home.views',
    (r'^$', 'home'),
)

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('website.profile.views',
    (r'^$', 'index'),
)

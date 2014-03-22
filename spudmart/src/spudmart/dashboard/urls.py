from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.dashboard.views',
    (r'^$', 'index')
)
from django.conf.urls.defaults import patterns

urlpatterns = patterns('website.spud.views',
    (r'^$', 'view'),
)

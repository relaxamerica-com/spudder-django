from django.conf.urls.defaults import patterns

urlpatterns = patterns('website.spudmart.views',
    (r'^$', 'home'),
    (r'^offer$', 'offer'),
)

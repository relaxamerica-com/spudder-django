from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.sponsors.views',
    (r'^(?P<page_id>\d+)$', 'public_view')
)
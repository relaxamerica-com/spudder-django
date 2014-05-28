from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.api.views',
    (r'^/', 'index'),
    (r'^get_venues/', 'get_venues'),
    (r'^save_posts_for_venue/', 'save_posts_for_venue'),
)

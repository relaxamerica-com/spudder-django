from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.sponsors.views',
    (r'^page$', 'sponsor_page'),
    (r'^page/remove_image/(?P<image_id>\d+)$', 'remove_image'),
    (r'^page/add_image$', 'add_image'),
)
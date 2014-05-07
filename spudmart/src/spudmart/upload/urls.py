from django.conf.urls.defaults import patterns

urlpatterns = patterns('spudmart.upload.views',
    (r'^get_upload_url$', 'get_upload_url'),
    (r'^upload_image_endpoint$', 'upload_image_endpoint'),
)
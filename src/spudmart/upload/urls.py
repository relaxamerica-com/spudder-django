from django.conf.urls.defaults import patterns

urlpatterns = patterns('spudmart.upload.views',
    (r'^get_upload_url$', 'get_upload_url'),
    (r'^upload_image_endpoint$', 'upload_image_endpoint'),
    (r'^get_croppic_upload$', 'get_croppic_upload'),
    (r'^croppic_upload_endpoint$', 'croppic_upload_endpoint'),
    (r'^croppic_crop$', 'croppic_crop'),
)
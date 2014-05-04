from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.files.views',
    (r'^serve/(?P<file_id>\d+)$', 'serve_uploaded_file'),
)
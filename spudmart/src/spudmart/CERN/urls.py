from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.CERN.views',
    (r'^(?P<state>\w{2})/(?P<school_name>[\w\ &-]+)/register/(?P<code>[\w\d\-]+)$', 'register_school'),
    (r'^(?P<state>\w{2})/(?P<school_name>[\w\ &-]+)/register/$', 'register_school'),
    (r'^(?P<state>\w{2})/(?P<school_name>[\w\ &-]+)/save$', 'save_school'),
    (r'^(?P<state>\w{2})/(?P<school_name>[\w\ &-]+)/$', 'school'),
    (r'^register/(?P<code>[\w\d\-]+)', 'register'),
    (r'^register$', 'register'),
    (r'^import_schools', 'import_school_data')
)
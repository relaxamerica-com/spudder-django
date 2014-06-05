from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.CERN.views',
    (r'^$', 'dashboard'),
    (r'^social_media/$', 'social_media'),
    (r'^content/$', 'content'),
    (r'^design/$', 'design'),
    (r'^testing/$', 'testing'),
    (r'^mobile/$', 'mobile'),
    (r'^add_email_alert/$', 'add_email_alert'),
    (r'^save_short_url/$', 'save_short_url'),
    (r'toggle_show/$', 'toggle_show'),
    
    
    # Registration & school pages
    (r'^(?P<state>\w{2})/(?P<school_name>[\w\ &-]+)/save$', 'save_school'),
    (r'^(?P<state>\w{2})/(?P<school_name>[\w\ &-]+)/(?P<code>[\w\d\-]+)$',
        'school', {'SSL' : True}),
    (r'^(?P<state>\w{2})/(?P<school_name>[\w\ &-]+)/$',
        'school', {'SSL' : True}),
    (r'^register/(?P<code>[\w\d\-]+)$', 'register'),
    (r'^register/$', 'register'),
    (r'^import_schools', 'import_school_data'),
    (r'^amazon_login/$', 'amazon_login'),
)

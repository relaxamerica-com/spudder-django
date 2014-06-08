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
    (r'^disable_about/$', 'disable_about'),
    
    
    # Registration & school pages
    (r'^(?P<state>\w{2})/(?P<school_name>[\w\ &-]+)/save_logo$',
        'save_school_logo'),
    (r'^(?P<state>\w{2})/(?P<school_name>[\w\ &-]+)/save$',
        'save_school'),
    (r'^(?P<state>\w{2})/(?P<school_name>[\w\ &-]+)/(?P<code>.+)$',
        'school', {'SSL_unauthenticated': True}),
    (r'^(?P<state>\w{2})/(?P<school_name>[\w\ &-]+)/$',
        'school', {'SSL_unauthenticated': True}),
    (r'^register/(?P<code>[\w\d\-]+)$', 'register'),
    (r'^register/$', 'register'),
    (r'^amazon_login/$', 'amazon_login'),
    (r'^import_schools', 'import_school_data'),
)

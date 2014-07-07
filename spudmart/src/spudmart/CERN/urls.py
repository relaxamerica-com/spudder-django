import os
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns


urlpatterns = patterns(
    'spudmart.CERN.views',
    url(r'^$', 'display_cern', name="cern_home"),
    url(r'^venues/$', 'venues'),
    url(r'^venues/new/$', 'venues_new'),
    url(r'^venues/delete/(?P<venue_id>\d+)$', 'delete_venue'),
    url(r'^social_media/$', 'social_media'),
    url(r'^content/$', 'content'),
    url(r'^design/$', 'design'),
    url(r'^testing/$', 'testing'),
    url(r'^mobile/$', 'mobile'),

    # Functional URLs url(limited to POST requests)
    url(r'^add_email_alert/$', 'add_email_alert'),
    url(r'^save_short_url/$', 'save_short_url'),
    url(r'^disable_about/$', 'disable_about'),
    url(r'^share/marketing_points$', 'share_marketing_points'),
    url(r'^share/social_media_points$', 'share_social_media_points'),
    url(r'^auto_share/marketing$', 'auto_share_marketing'),
    url(r'^auto_share/social_media$', 'auto_share_social_media'),
    url(r'^auto_share/marketing_level$', 'auto_share_marketing_level'),
    url(r'^auto_share/social_media_level$', 'auto_share_social_media_level'),
    # This is a handler for the LinkedIn Response, and is limited to GETs
    url(r'^save_linkedin$', 'save_linkedin'),


    # Registration & school pages
    url(r'^(?P<school_id>\d+)/save_logo$', 'save_school_logo'),
    url(r'^(?P<school_id>\d+)/save$', 'save_school'),
    url(r'^(?P<school_id>\d+)/register/(?P<referral_id>.+)$', 'register_school',
        {'SSL': False if os.environ['SERVER_SOFTWARE'].startswith('Development') else True}),
    url(r'^(?P<school_id>\d+)/register/$', 'register_school',
        {'SSL': False if os.environ['SERVER_SOFTWARE'].startswith('Development') else True}),
    url(r'^(?P<state>\w{2})/(?P<school_id>\d+)/(?P<name>[^/]+)/(?P<referral_id>.+)$',
        'school'),
    url(r'^(?P<state>\w{2})/(?P<school_id>\d+)/(?P<name>[^/]+)/$',
        'school'),
    url(r'^register/(?P<referral_id>[\w\d\-]+)$', 'register'),
    url(r'^register/$', 'register'),
    # url(r'^amazon_login/$', 'amazon_login'),
    url(r'^join_school/(?P<school_id>\d+)/(?P<referral_id>\d+)$', 'join_school'),
    url(r'^join_school/(?P<school_id>\d+)/$', 'join_school'),

    url(r'login/$', 'login', {'SSL': True}),

    # Link for queue url(it's protected)
    url(r'^import_schools$', 'import_school_data'),
    url(r'^import_schools_async$', 'import_school_data_async'),

    # Link for decorator error page
    url(r'^non-student/$', 'user_not_student_error_page')
)

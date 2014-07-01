import os
from django.conf.urls.defaults import patterns


urlpatterns = patterns(
    'spudmart.CERN.views',
    (r'^$', 'display_cern'),
    (r'^venues/$', 'venues'),
    (r'^venues/new/$', 'venues_new'),
    (r'^venues/delete/(?P<venue_id>\d+)$', 'delete_venue'),
    (r'^social_media/$', 'social_media'),
    (r'^content/$', 'content'),
    (r'^design/$', 'design'),
    (r'^testing/$', 'testing'),
    (r'^mobile/$', 'mobile'),

    # Functional URLs (limited to POST requests)
    (r'^add_email_alert/$', 'add_email_alert'),
    (r'^save_short_url/$', 'save_short_url'),
    (r'^disable_about/$', 'disable_about'),
    (r'^share/marketing_points$', 'share_marketing_points'),
    (r'^share/social_media_points$', 'share_social_media_points'),
    (r'^auto_share/marketing$', 'auto_share_marketing'),
    (r'^auto_share/social_media$', 'auto_share_social_media'),
    (r'^auto_share/marketing_level$', 'auto_share_marketing_level'),
    (r'^auto_share/social_media_level$', 'auto_share_social_media_level'),
    # This is a handler for the LinkedIn Response, and is limited to GETs
    (r'^save_linkedin$', 'save_linkedin'),


    # Registration & school pages
    (r'^(?P<school_id>\d+)/save_logo$', 'save_school_logo'),
    (r'^(?P<school_id>\d+)/save$', 'save_school'),
    (r'^(?P<school_id>\d+)/register/(?P<referral_id>.+)$', 'register_school',
        {'SSL_unauthenticated': False if os.environ['SERVER_SOFTWARE'].startswith('Development') else True}),
    (r'^(?P<school_id>\d+)/register/$', 'register_school',
        {'SSL_unauthenticated': False if os.environ['SERVER_SOFTWARE'].startswith('Development') else True}),
    (r'^(?P<state>\w{2})/(?P<school_id>\d+)/(?P<name>[^/]+)/(?P<referral_id>.+)$',
        'school'),
    (r'^(?P<state>\w{2})/(?P<school_id>\d+)/(?P<name>[^/]+)/$',
        'school'),
    (r'^register/(?P<referral_id>[\w\d\-]+)$', 'register'),
    (r'^register/$', 'register'),
    # (r'^amazon_login/$', 'amazon_login'),
    (r'^join_school/(?P<school_id>\d+)/(?P<referral_id>\d+)$', 'join_school'),
    (r'^join_school/(?P<school_id>\d+)/$', 'join_school'),

    (r'login/$', 'login', {'SSL': True}),

    # Link for queue (it's protected)
    (r'^import_schools$', 'import_school_data'),
    (r'^import_schools_async$', 'import_school_data_async'),

    # Link for decorator error page
    (r'^non-student/$', 'user_not_student_error_page')
)

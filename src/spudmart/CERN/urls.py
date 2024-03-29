import os
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns


urlpatterns = patterns(
    'spudmart.CERN.views',
    url(r'^$', 'display_cern', name="cern_home"),
    url(r'^venues/$', 'venues'),
    url(r'^venues/new/$', 'venues_new'),
    url(r'^venues/create_temp$', 'create_temp_venue'),
    url(r'^venues/venue_created/(?P<venue_id>\d+)$', 'venue_created'),
    url(r'^venues/temp_view/(?P<venue_id>\d+)$', 'temp_venue_view'),
    url(r'^venues/delete/(?P<venue_id>\d+)$', 'delete_venue'),
    url(r'^venues/publish/(?P<venue_id>\d+)$', 'publish_venue'),
    url(r'^social_media/$', 'social_media'),
    url(r'^content/$', 'content'),
    url(r'^design/$', 'design'),
    url(r'^testing/$', 'testing'),
    url(r'^mobile/$', 'mobile'),

    # For student pages
    url(r'^student/(?P<student_id>\d+)$', 'student_page'),
    url(r'^student/(?P<student_id>\d+)/save_cover$', 'save_student_cover'),
    url(r'^student/(?P<student_id>\d+)/reset_cover$', 'reset_student_cover'),
    url(r'^student/(?P<student_id>\d+)/edit_cover', 'edit_student_cover'),
    url(r'^student/(?P<student_id>\d+)/save_logo$', 'save_student_logo'),
    url(r'^student/(?P<student_id>\d+)/save_social_media$', 'save_student_social_media'),
    url(r'^student/(?P<student_id>\d+)/upload_resume$', 'upload_student_resume'),
    url(r'^student/(?P<student_id>\d+)/apply_qa$', 'apply_qa'),
    url(r'^student/(?P<student_id>\d+)/delete_resume$', 'delete_resume'),
    url(r'^student/(?P<student_id>\d+)/send_help_message$', 'send_help_message'),

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

    # School pages
    url(r'^(?P<school_id>\d+)/save_logo$', 'save_school_logo'),
    url(r'^(?P<school_id>\d+)/save$', 'save_school'),
    url(r'^(?P<school_id>\d+)/save_school_cover$', 'save_school_cover'),
    url(r'^(?P<school_id>\d+)/edit_cover_image$', 'edit_school_cover'),
    url(r'^(?P<school_id>\d+)/reset_school_cover$', 'reset_school_cover'),
    url(r'^(?P<state>\w{2})/(?P<school_id>\d+)/(?P<name>[^/]+)/(?P<referral_id>.+)$',
        'school'),
    url(r'^(?P<state>\w{2})/(?P<school_id>\d+)/(?P<name>[^/]+)/$',
        'school'),

    # Registration pages
    url(r'^(?P<school_id>\d+)/register/(?P<referral_id>.+)$', 'register_school'),
    url(r'^(?P<school_id>\d+)/register/$', 'register_school'),
    url(r'^register/(?P<referral_id>[\w\d\-]+)$', 'register'),
    url(r'^register/$', 'register'),
    url(r'^register$', 'register'),
    url(r'^register/tcs_required/$', 'tcs_required'),
    url(r'^register/choose_school/(?P<referral_id>.+)$', 'choose_school'),
    url(r'^register/choose_school/$', 'choose_school'),
    url(r'^register/choose_state/(?P<referral_id>.+)$', 'choose_state'),
    url(r'^register/choose_state/$', 'choose_state'),
    url(r'^register/(?P<state>\w{2})/choose_school/(?P<referral_id>.+)',
        'choose_school_from_state'),
    url(r'^register/(?P<state>\w{2})/choose_school/$', 'choose_school_from_state'),

    url(r'^join_school/(?P<school_id>\d+)/(?P<referral_id>\d+)$', 'join_school'),
    url(r'^join_school/(?P<school_id>\d+)/$', 'join_school'),
    url(r'^join_cern$', 'cern_splash'),

    # Links for queueing
    url(r'^import_schools$', 'import_school_data'),
    url(r'^import_schools_async$', 'import_school_data_async'),
    url(r'^import_school_addrs$', 'import_school_addrs'),
    url(r'^import_school_addrs_async$', 'import_school_addrs_async'),
    url(r'^translate_referrals$', 'translate_referrals'),
    url(r'^translate_referrals_async$', 'translate_referrals_async'),
    url(r'^remove_student_sessions$', 'remove_student_sessions'),
    url(r'^remove_student_sessions_async$', 'remove_student_sessions_async'),

    # Link for decorator error page
    url(r'^non-student$', 'user_not_student_error_page'),

    url(r'^compensation$', 'compensation'),
    url(r'^redeem_points$', 'redeem_points'),
    url(r'^after_college$', 'after_college'),
    url(r'^signin$', 'student_login'),
    url(r'^login$', 'student_login'),
    url(r'^login/migrate$', 'migrate_from_amazon'),

)

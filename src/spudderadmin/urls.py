from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderadmin.views',

    url('^/dashboard', 'admin_dashboard'),
    
    url('^/cern/qa_job_board$', 'qa_job_board'),
    url('^/cern/students$', 'students'),
    url('^/cern/student/(?P<student_id>\d+)/resume$', 'student_resume'),
    url('^/cern/student/(?P<student_id>\d+)/accept$', 'accept_student'),
    url('^/cern/student/(?P<student_id>\d+)/reject$', 'reject_student'),
    url('^/cern/student/(?P<student_id>\d+)/waitlist$', 'waitlist_student'),
    url('^/cern/student/(?P<student_id>\d+)/send_email$','send_student_email'),
    url('^/cern/schools$', 'schools'),
    url('^/cern', 'cern_dashboard'),


    url(r'^/socialengine/atpostspud$', 'socialengine_atpostspud'),
    url(r'^/socialengine/location_scraper$', 'socialengine_location_scraper'),
    url(r'^/socialengine', 'socialengine_dashboard'),

    url(r'^/system/teams$', 'system_teams'),
    url(r'^/system/venues$', 'system_venues'),
    url(r'^/system/nukedb$', 'system_nukedb'),
    url(r'^/system/school_covers$', 'system_remove_school_cover_images'),
    url(r'^/system', 'system_dashboard'),

    url(r'^/reports/fans$', 'fan_reports'),
    url(r'^/reports/fans/(?P<fan_id>\d+)/send_email$','send_fan_email'),
    url(r'^/reports/sponsors$', 'sponsor_reports'),
    url(r'^/reports/sponsors/(?P<sponsor_id>\d+)/sponsorships$', 'sponsorships'),
    url(r'^/reports/sponsors/all_sponsorships$', 'all_sponsorships'),
    url(r'^/reports/sponsors/(?P<sponsor_id>\d+)/send_email', 'send_sponsor_email'),
    url(r'^/reports/teams$', 'teams'),
    url(r'^/reports/teams/(?P<admin_id>\d+)/send_admin_email$','send_team_admin_email'),
    url(r'^/reports/venues$', 'all_venues'),
    url(r'^/reports/venues/(?P<venue_id>\d+)/spuds','spuds_for_venue'),
    url(r'^/reports/venues/map', 'venues_map_landing'),
    url(r'^/reports/venues/(?P<sport>.+)/map', 'venues_map_by_sport'),
    url(r'^/reports', 'user_reports_dashboard'),

    url(r'^/affiliates/create$', 'create_affiliate'),
    url(r'^/affiliates/edit/(?P<affiliate_id>\d+)$', 'edit_affiliate'),
    url(r'^/affiliates/confirm_delete/(?P<affiliate_id>\d+)$', 'confirm_delete'),
    url(r'^/affiliates/delete/(?P<affiliate_id>\d+)$','delete_affiliate'),
    url(r'^/affiliates', 'affiliates'),

    url(r'^/send_email$', 'send_email'),

    url(r'^/challenges$', 'challenges'),

    url(r'^', 'admin_login'),
)
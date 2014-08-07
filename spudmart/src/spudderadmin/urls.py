from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderadmin.views',

    url('^/dashboard', 'admin_dashboard'),
    
    url('^/cern/$', 'cern_dashboard'),
    url('^/cern/qa_job_board$', 'qa_job_board'),
    url('^/cern/student/(?P<student_id>\d+)/resume$', 'student_resume'),
    url('^/cern/student/(?P<student_id>\d+)/accept$', 'accept_student'),
    url('^/cern/student/(?P<student_id>\d+)/reject$', 'reject_student'),
    url('^/cern/student/(?P<student_id>\d+)/waitlist$', 'waitlist_student'),

    url(r'^/socialengine', 'socialengine_dashboard'),
    url(r'^/system/nukedb', 'system_nukedb'),
    url(r'^/system/school_covers', 'system_remove_school_cover_images'),
    url(r'^/system', 'system_dashboard'),

    url('^', 'admin_login'),
)
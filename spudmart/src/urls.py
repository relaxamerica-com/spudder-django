from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns(
    '',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    ('^_ah/start$', 'spudmart.utils.backends.start'),
    # (r'^$', include('spudmart.home.urls')),  NOTE: Commented out by MG 20140617
    (r'^dashboard/recipient/', include('spudmart.recipients.urls')),
    (r'^dashboard/donation/', include('spudmart.donations.urls')),
    (r'^dashboard/sponsor/', include('spudmart.sponsors.urls')),
    (r'^dashboard/', include('spudmart.dashboard.urls')),
    (r'^accounts/', include('spudmart.accounts.urls')),
    (r'^venues/', include('spudmart.venues.urls')),
    (r'^spudder/', include('spudmart.spudder.urls')),
    (r'^upload/', include('spudmart.upload.urls')),
    (r'^sponsor/', include('spudmart.sponsors.public_urls')),
    (r'^hospitals/', include('spudmart.hospitals.urls')),
    (r'^file/serve/(?P<file_id>\d+)$', 'spudmart.upload.views.serve_uploaded_file'),
    (r'^api/1/', include('spudmart.api.urls')),

    (r'^cern/', include('spudmart.CERN.urls')),

    # Note the below line was added to catch root urls and push them to CERN, MG 20140617
    (r'^$', redirect_to, {'url': '/cern'})
)

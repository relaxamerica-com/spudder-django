from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    (r'^$', include('spudmart.home.urls')),
    (r'^file/serve/(?P<file_id>\d+)$', 'spudmart.upload.views.serve_blob'),
    (r'^dashboard/recipient/', include('spudmart.recipients.urls')),
    (r'^dashboard/donation/', include('spudmart.donations.urls')),
    (r'^dashboard/', include('spudmart.dashboard.urls')),
    (r'^accounts/', include('spudmart.accounts.urls')),
    (r'^venues/', include('spudmart.venues.urls')),
    (r'^upload/', include('spudmart.upload.urls')),
)

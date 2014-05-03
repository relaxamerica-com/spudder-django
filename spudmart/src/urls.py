from django.conf.urls.defaults import *


handler404 = 'django.views.defaults.page_not_found'
handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    ('^_ah/start$', 'spudmart.utils.backends.start'),
    (r'^$', include('spudmart.home.urls')),
    (r'^dashboard/recipient/', include('spudmart.recipients.urls')),
    (r'^dashboard/donation/', include('spudmart.donations.urls')),
    (r'^dashboard/', include('spudmart.dashboard.urls')),
    (r'^accounts/', include('spudmart.accounts.urls')),
    (r'^spudder/', include('spudmart.spudder.urls')),
)

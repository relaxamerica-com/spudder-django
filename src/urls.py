from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    (r'^$', include('website.home.urls')),
    (r'^accounts/', include('registration.urls')),
    (r'^league_or_tournament/', include('website.league_or_tournament.urls'))
)

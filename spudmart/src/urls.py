from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    (r'^$', include('spudmart.home.urls')),
    (r'^dashboard/', include('spudmart.dashboard.urls')),
    (r'^accounts/', include('registration.urls')),
)
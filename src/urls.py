from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    (r'^$', include('website.home.urls')),
    (r'^accounts/', include('registration.urls')),
    (r'^tournament/', include('website.tournament.urls')),
    (r'^league/', include('website.league.urls')),
    (r'^profile/', include('website.profile.urls')),
    (r'^fan/', include('website.fan.urls')),
    (r'^sponsors/', include('website.sponsors.urls')),
    (r'^spud/', include('website.spud.urls')),
    (r'^spudmart/', include('website.spudmart.urls'))
)

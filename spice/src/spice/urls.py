from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from spice.api import *

urlpatterns = patterns('',
                       # Home page
                       url(r'^$', 'spice.views.home', name='home'),

                       # API handlers
                       url(r'^api/location', location),
                       url(r'^api/', api_landing),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       # url(r'^admin/', include(admin.site.urls)),
)

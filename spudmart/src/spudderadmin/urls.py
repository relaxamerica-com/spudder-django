from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderadmin.views',

    url(r'^/dashboard', 'admin_dashboard'),
    url(r'^/cern', 'cern_dashboard'),
    url(r'^/socialengine', 'socialengine_dashboard'),
    url(r'^/system/nukedb', 'system_nukedb'),
    url(r'^/system', 'system_dashboard'),
    url(r'^', 'admin_login'),
)
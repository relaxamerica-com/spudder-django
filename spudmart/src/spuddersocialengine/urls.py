from django.conf.urls.defaults import patterns, include, url
from spuddersocialengine.api import *

urlpatterns = patterns(
    '',

    # API handlers
    url(r'^api/location$', location),
    url(r'^api/location_task$', location_task),
    url(r'^api/manual_process$', manual_process),
    url(r'^api/$', api_landing),
    url(r'^api/instagram/', include('spuddersocialengine.socialnetworks.instagram_urls')),
)

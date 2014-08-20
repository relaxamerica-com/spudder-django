from django.conf.urls.defaults import patterns, url
from spuddersocialengine.locationscraper.api import *
from spuddersocialengine.locationscraper.socialnetworks.instagram import callback, callback_task
from atpostspud.views import tick, get_latest_at_post_spuds_view


urlpatterns = patterns(
    '',
    # API handlers
    url(r'^api/location$', location),
    url(r'^api/location_task$', location_task),
    url(r'^api/manual_process$', manual_process),
    url(r'^api/$', api_landing),
    url(r'^api/instagram/callback$', callback),
    url(r'^api/instagram/callback_task$', callback_task),

    #@postspud handlers
    url(r'^postspud/tick', tick),
    url(r'^postspud/get_latest_at_post_spuds', get_latest_at_post_spuds_view),
)

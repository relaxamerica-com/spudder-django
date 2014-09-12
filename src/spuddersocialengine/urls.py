from django.conf.urls.defaults import patterns, url
from spuddersocialengine.locationscraper import api
from spuddersocialengine.locationscraper.socialnetworks.instagram import callback, callback_task
from atpostspud.views import tick, get_latest_at_post_spuds_view


urlpatterns = patterns(
    '',
    # API handlers
    url(r'^api/location$', api.location),
    url(r'^api/location_task$', api.location_task),
    url(r'^api/manual_process$', api.manual_process),
    url(r'^api/$', api.api_landing),
    url(r'^api/instagram/callback/(?P<sport>\w+)$', callback),
    url(r'^api/instagram/callback_task$', callback_task),

    #@postspud handlers
    url(r'^postspud/tick', tick),
    url(r'^postspud/get_latest_at_post_spuds', get_latest_at_post_spuds_view),
)

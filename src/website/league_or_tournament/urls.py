
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('website.league_or_tournament.views',
       (r'^$', 'league_or_tournament'),
)


from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('website.league.views',
       (r'^$', 'league_or_tournament'),
)

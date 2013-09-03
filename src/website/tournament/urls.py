
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('website.tournament.views',
       (r'^$', 'league_or_tournament'),
)

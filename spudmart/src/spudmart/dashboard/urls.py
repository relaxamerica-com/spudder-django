from django.conf.urls.defaults import patterns
from django.views.generic.base import TemplateView


urlpatterns = patterns('spudmart.dashboard.views',
    (r'^$', 'index'),
    (r'^recipient/(?P<team_id>[a-zA-Z0-9_]+)/complete$', 'recipient_complete'),
    (r'^recipient/(?P<team_id>[a-zA-Z0-9_]+)/thanks$', 'recipient_thanks'),
    (r'^recipient/(?P<team_id>[a-zA-Z0-9_]+)/error$', 'recipient_error'),
    (r'^recipient/(?P<team_id>[a-zA-Z0-9_]+)/$', 'recipient'),
)
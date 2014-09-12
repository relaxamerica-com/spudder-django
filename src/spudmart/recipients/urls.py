from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.recipients.views',
    (r'^(?P<team_id>[a-zA-Z0-9_]+)/$', 'index'),
    (r'^(?P<team_id>[a-zA-Z0-9_]+)/complete$', 'complete'),
    (r'^(?P<team_id>[a-zA-Z0-9_]+)/thanks$', 'thanks'),
    (r'^(?P<team_id>[a-zA-Z0-9_]+)/error$', 'error'),
)
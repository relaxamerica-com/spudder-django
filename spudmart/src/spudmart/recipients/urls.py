from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.recipients.views',
    (r'^(?P<team_id>[a-zA-Z0-9_]+)/$', 'recipient'),
    (r'^(?P<team_id>[a-zA-Z0-9_]+)/complete$', 'recipient_complete'),
    (r'^(?P<team_id>[a-zA-Z0-9_]+)/thanks$', 'recipient_thanks'),
    (r'^(?P<team_id>[a-zA-Z0-9_]+)/error$', 'recipient_error'),
)
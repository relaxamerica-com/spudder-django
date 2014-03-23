from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.donations.views',
    (r'^(?P<offer_id>[a-zA-Z0-9_]+)/$', 'index'),
    (r'^(?P<donation_id>[a-zA-Z0-9_]+)/complete$', 'complete'),
    (r'^(?P<donation_id>[a-zA-Z0-9_]+)/thanks$', 'thanks')
)
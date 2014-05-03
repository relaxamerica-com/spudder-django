from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.spudder.views',
    (r'^synchronise_sponsorship_data_from_donation/(?P<donation_id>[a-zA-Z0-9_]+)$', 'synchronise_sponsorship_data_from_donation'),
)
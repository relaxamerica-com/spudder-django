from django.conf.urls.defaults import *


urlpatterns = patterns('spudmart.challenges.views',
    (r'^$', 'get_challenges'),
    (r'^create/$', 'new_challenge_wizard_view'),
)

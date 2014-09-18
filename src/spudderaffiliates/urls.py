from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderaffiliates.views',

    url(r'^/dashboard$', 'affiliate_dashboard'),
    url(r'^/invite_club_managers', 'invite_club_manager'),
    url(r'^/invitation$', 'invitation'),

    url(r'^', 'affiliate_login'),
)
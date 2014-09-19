from django.conf.urls.defaults import *

urlpatterns = patterns(
    'spudderaffiliates.views',

    url(r'^/dashboard$', 'affiliate_dashboard'),
    url(r'^/invite_club_managers', 'invite_club_manager'),
    url(r'^/invitation/(?P<invitation_id>\d+)$', 'invitation'),
    url(r'^/invitation/(?P<invitation_id>\d+)/redirect_to_registration$', 'redirect_to_registration'),
    url(r'^/invitation/(?P<invitation_id>\d+)/create_club$', 'create_invited_club'),
    url(r'^/invitation/(?P<invitation_id>\d+)/incorrect_name$', 'incorrect_name'),
    url(r'^/invitation/(?P<invitation_id>\d+)/create_team$', 'create_team'),

    url(r'^', 'affiliate_login'),
)
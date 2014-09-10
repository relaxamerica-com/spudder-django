from django.conf.urls.defaults import patterns


urlpatterns = patterns(
    'spudmart.teams.views',
    (r'^list$', 'teams_list'),
    (r'^create$', 'create_team'),
    (r'^page/(?P<page_id>\d+){0,1}$', 'team_page'),
    (r'^(?P<page_id>\d+)$', 'public_view'),
    (r'^(?P<page_id>\d+)/edit$', 'edit_team_page'),
    (r'^(?P<page_id>\d+)/admins$', 'manage_team_page_admins'),
    (r'^(?P<page_id>\d+)/invite_fan/(?P<fan_id>\d+)$', 'create_fan_invitation'),
    (r'^(?P<page_id>\d+)/cancel_fan_invitation/(?P<fan_id>\d+)$', 'cancel_fan_invitation'),
    (r'^(?P<page_id>\d+)/revoke_fan_invitation/(?P<fan_id>\d+)$', 'revoke_fan_invitation'),
    (r'^(?P<page_id>\d+)/accept_fan_invitation/(?P<invitation_id>\d+)$', 'accept_fan_invitation'),
    (r'^remove_image$', 'remove_image'),
    (r'^search$', 'search_teams'),
    (r'^(?P<page_id>\d+)/edit_cover$', 'edit_cover'),
    (r'^(?P<page_id>\d+)/save_cover$', 'save_cover'),
    (r'^(?P<page_id>\d+)/reset_cover$', 'reset_cover'),
    (r'^(?P<page_id>\d+)/save_avatar$', 'save_avatar'),
    (r'^associate/(?P<page_id>\d+)$', 'associate_with_venue'),
    (r'^associate/(?P<page_id>\d+)/(?P<venue_id>\d+)$', 'associate_team_with_venue'),
    (r'^associate/(?P<page_id>\d+)/remove/(?P<venue_id>\d+)$', 'remove_association_with_venue'),
    (r'^send_message/(?P<page_id>\d+)$', 'send_message'),
)
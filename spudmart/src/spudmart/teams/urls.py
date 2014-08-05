from django.conf.urls.defaults import patterns


urlpatterns = patterns(
    'spudmart.teams.views',
    (r'^list$', 'teams_list'),
    (r'^page/(?P<page_id>\d+){0,1}$', 'team_page'),
    (r'^(?P<page_id>\d+)$', 'public_view'),
    (r'^remove_image$', 'remove_image'),
)
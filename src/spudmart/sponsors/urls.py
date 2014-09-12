from django.conf.urls.defaults import patterns
from django.views.generic import TemplateView


urlpatterns = patterns(
    'spudmart.sponsors.views',
    (r'^/page$', 'sponsor_page'),
    (r'^/save_cover/(?P<page_id>\d+)$', 'save_cover'),
    (r'^/reset_cover/(?P<page_id>\d+)$', 'reset_cover'),
    (r'^/edit_cover/(?P<page_id>\d+)$', 'edit_cover'),
    (r'^/save_logo_and_name/(?P<page_id>\d+)$', 'save_logo_and_name'),
    (r'^/(?P<page_id>\d+)$', 'public_view'),
    (r'^/venues/$', 'sponsors_venues'),
    (r'^_network$', 'sponsors_splash'),
    (r'^/register$', 'user_register', {'SSL': True}),
    (r'^/signin$', 'user_signin', {'SSL': True}),
    (r'^/non_sponsor$', TemplateView.as_view(template_name='spuddersponsors/pages/non_sponsor.html')),
    (r'^/$', 'sponsors_dashboard'),
)
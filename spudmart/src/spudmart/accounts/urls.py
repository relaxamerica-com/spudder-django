from django.conf.urls.defaults import patterns
from django.views.generic.base import TemplateView


urlpatterns = patterns('spudmart.accounts.views',
    (r'^login/$', 'login', {'SSL' : True}),
    (r'^login/amazon$', 'amazon_login'),
    (r'^login/just_login$', 'just_login'),
    (r'^amazon_required/$', 'amazon_required'),
    (r'^logout/$', 'logout'),
    (r'^fix_accounts$', 'fix_accounts'),

    # This was added so that local fake login can take place
    (r'^login_fake/$', 'login_fake'),

)
import os
from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.accounts.views',
    (r'^login/$', 'login', {'SSL' : True}),
    (r'^login/amazon$', 'amazon_login'),
    (r'^login/just_login$', 'just_login'),
    (r'^amazon_required/$', 'amazon_required'),
    (r'^logout/$', 'logout'),
    (r'^fix_accounts$', 'fix_accounts'),
    (r'^login/sponsors$', 'sponsor_login',
        {'SSL': False if os.environ['SERVER_SOFTWARE'].startswith('Development') else True}),

    # This was added so that local fake login can take place
    (r'^login_fake/$', 'login_fake'),

)
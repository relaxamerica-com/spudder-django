import os
from django.conf.urls.defaults import patterns


in_dev = os.environ['SERVER_SOFTWARE'].startswith('Development')
urlpatterns = patterns(
    'spudmart.accounts.views',
    (r'^login/amazon', 'amazon_login'),
    (r'^login/just_login', 'just_login'),
    (r'^login/sponsors', 'sponsor_login', {'SSL': False if in_dev else True}),
    (r'^login/fans', 'fan_login', {'SSL': False if in_dev else True}),
    (r'^login', 'login', {'SSL' : True}),
    (r'^logout', 'logout'),

    (r'^amazon_required', 'amazon_required'),
    (r'^fix_accounts$', 'fix_accounts'),

    # This was added so that local fake login can take place
    (r'^login_fake/$', 'login_fake'),

)
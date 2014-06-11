from django.conf.urls.defaults import patterns
from django.views.generic.base import TemplateView


urlpatterns = patterns('spudmart.accounts.views',
    (r'^login/$', 'login', {'SSL' : True}),
    (r'^login/amazon$', 'amazon_login'),
    (r'^login/just_login$', 'just_login'),

    (r'^logout/$', 'logout'),
    (r'^fix_accounts$', 'fix_accounts'),
)
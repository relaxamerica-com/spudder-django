from django.conf.urls.defaults import patterns
from django.views.generic.base import TemplateView


urlpatterns = patterns('spudmart.accounts.views',
    (r'^login/$', 'login'),
    (r'^login/amazon$', 'amazon_login'),
    (r'^logout/$', 'logout')
)
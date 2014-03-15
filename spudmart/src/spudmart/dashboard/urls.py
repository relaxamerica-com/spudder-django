from django.conf.urls.defaults import patterns
from django.views.generic.base import TemplateView


urlpatterns = patterns('spudmart.dashboard.views',
    (r'^$', 'index')
)
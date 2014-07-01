from django.conf.urls.defaults import patterns
from django.views.generic.base import TemplateView


urlpatterns = patterns('spudmart.home.views',
    (r'^$', TemplateView.as_view(template_name='old/home/index.html'))
)
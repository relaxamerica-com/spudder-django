from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns


urlpatterns = patterns(
    'spudmart.flags.views',
    url(r'^test$', 'test'),
    url(r'^flag$', 'flag_page'),
)

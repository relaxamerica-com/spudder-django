from django.conf.urls.defaults import *

urlpatterns = patterns('spudderstripe.views',

    (r'webhook$', 'webhook'),
)
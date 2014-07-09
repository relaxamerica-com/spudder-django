from django.conf.urls.defaults import patterns, include, url

from instagram import *

urlpatterns = patterns('',
                       # URL handlers
                       url(r'^callback$', callback),
                       url(r'^callback_task$', callback_task),
)

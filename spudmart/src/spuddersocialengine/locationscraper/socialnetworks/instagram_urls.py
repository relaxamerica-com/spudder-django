from django.conf.urls.defaults import patterns, url

from spuddersocialengine.locationscraper.socialnetworks.instagram import *

urlpatterns = patterns('',
                       # URL handlers
                       url(r'^callback$', callback),
                       url(r'^callback_task$', callback_task),
)

from django.conf.urls.defaults import patterns, url
from django.contrib import admin

urlpatterns = patterns('website.home.views',
    (r'^$', 'home'),
)

from django.conf.urls.defaults import *


urlpatterns = patterns('spudmart.challenges.views',
    (r'^$', 'get_challenges'),
    (r'^(?P<challenge_id>\d+)$', 'view_challenge'),
    (r'^template/(?P<template_id>\d+)$', 'view_challenge_template'),
    (r'^template/(?P<template_id>\d+)/edit$', 'edit_challenge_template'),
    (r'^create$', 'new_challenge_wizard_view'),
)

from django.conf.urls.defaults import *
from spudderdomain.models import TempClub, Club

urlpatterns = patterns(
    'spudderspuds.challenges.views',

    url(r'(?P<challenge_id>\d+)/share',
        'challenge_share'),

    url(r'(?P<challenge_id>\d+)',
        'challenge_view'),

    url(r'create/(?P<template_id>\d+)/(?P<state>\w+)/o/(?P<club_id>\d+)$',
        'create_challenge_set_donation',
        {'club_class': Club}),

    url(r'create/(?P<template_id>\d+)/(?P<state>\w+)/t/(?P<club_id>\d+)$',
        'create_challenge_set_donation',
        {'club_class': TempClub}),

    url(r'create/(?P<template_id>\d+)/(?P<state>\w+)/create_club$',
        'create_challenge_choose_club_create_club'),

    url(r'create/(?P<template_id>\d+)/(?P<state>\w+)$',
        'create_challenge_choose_club'),

    url(r'create/(?P<template_id>\d+)$',
        'create_challenge_choose_club_choose_state'),

    url(r'create/signin$',
        'create_signin'),

    url(r'create/register$',
        'create_register'),

    url(r'create$',
        'create_challenge'),
)

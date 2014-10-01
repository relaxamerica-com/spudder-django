from django.conf.urls.defaults import *
from spudderdomain.controllers import EntityController
from spudderdomain.models import TempClub, Club

urlpatterns = patterns(
    'spudderspuds.challenges.views',

    url(r'signin$',
        'create_signin'),

    url(r'register$',
        'create_register'),

    url(r'register/team$',
        'register_club'),

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

    url(r'create$',
        'create_challenge'),

    url(r'(?P<participation_id>\d+)/beneficiary/(?P<state>\w+)/o/(?P<club_id>\d+)$',
        'challenge_accept_beneficiary_set_donation',
        {'club_class': Club}),

    url(r'(?P<participation_id>\d+)/beneficiary/(?P<state>\w+)/t/(?P<club_id>\d+)$',
        'challenge_accept_beneficiary_set_donation',
        {'club_class': TempClub}),

    url(r'(?P<participation_id>\d+)/beneficiary/(?P<state>\w+)/create_club$',
        'challenge_accept_beneficiary_create_club'),

    url(r'(?P<participation_id>\d+)/beneficiary/(?P<state>\w+)$',
        'challenge_accept_beneficiary'),

    url(r'(?P<participation_id>\d+)/state$',
        'challenge_accept_state'),

    url(r'challenge_challenge/(?P<participation_id>\d+)/upload$',
        'challenge_challenge_accept_notice'),

    url(r'challenge_challenge/beneficiary/(?P<state>\w+)/clubs/o/(?P<club_id>\d+)$',
        'challenge_challenge_accept_notice',
        {'club_entity_type': EntityController.ENTITY_CLUB}),

    url(r'challenge_challenge/beneficiary/(?P<state>\w+)/clubs/t/(?P<club_id>\d+)$',
        'challenge_challenge_accept_notice',
        {'club_entity_type': EntityController.ENTITY_TEMP_CLUB}),

    url(r'challenge_challenge/beneficiary/(?P<state>\w+)/clubs/create_club$',
        'challenge_challenge_accept_beneficiary_create_club'),
    
    url(r'challenge_challenge/beneficiary/(?P<state>\w+)/clubs$',
        'challenge_challenge_accept_beneficiary_load_clubs'),

    url(r'challenge_challenge/beneficiary/(?P<state>\w*)$',
        'challenge_challenge_accept_beneficiary'),

    url(r'challenge_challenge/(?P<participation_id>\d+)/thanks$',
        'challenge_challenge_thanks'),

    url(r'challenge_challenge$',
        'challenge_challenge'),

    url(r'(?P<challenge_id>\d+)/accept/notice$',
        'challenge_accept_notice'),

    url(r'(?P<challenge_id>\d+)/accept/pledge$',
        'challenge_accept_pledge'),

    url(r'(?P<challenge_id>\d+)/accept$',
        'challenge_accept_upload'),

    url(r'(?P<challenge_id>\d+)/share$',
        'challenge_share'),

    url(r'(?P<challenge_id>\d+)$',
        'challenge_view'),

    url(r'^tick',
        'tick'),
    
    url(r'^send_challenge_emails', 
        'send_challenge_emails'),

    url(r'$',
        'challenges_splash'),
)

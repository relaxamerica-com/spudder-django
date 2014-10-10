from django.conf.urls.defaults import *
from spudderdomain.controllers import EntityController
from spudderdomain.models import TempClub, Club
from spudmart.utils.url import determine_ssl

urlpatterns = patterns(
    'spudderspuds.challenges.views',

    url(r'signin$',
        'signin', {'SSL': determine_ssl()}),

    url(r'register$',
        'register', {'SSL': determine_ssl()}),

    url(r'register/team$',
        'register_club', {'SSL': determine_ssl()}),

    url(r'create/(?P<template_id>\d+)/(?P<state>\w+)/o/(?P<club_id>\d+)$',
        'create_challenge_set_donation',
        {'club_class': Club, 'SSL': determine_ssl()}),

    url(r'create/(?P<template_id>\d+)/(?P<state>\w+)/t/(?P<club_id>\d+)$',
        'create_challenge_set_donation',
        {'club_class': TempClub, 'SSL': determine_ssl()}),

    url(r'create/(?P<template_id>\d+)/(?P<state>\w+)/create_club$',
        'create_challenge_choose_club_create_club', {'SSL': determine_ssl()}),

    url(r'create/(?P<template_id>\d+)/(?P<state>\w+)$',
        'create_challenge_choose_club', {'SSL': determine_ssl()}),

    url(r'create/(?P<template_id>\d+)$',
        'create_challenge_choose_club_choose_state', {'SSL': determine_ssl()}),

    url(r'create$',
        'create_challenge', {'SSL': determine_ssl()}),

    url(r'(?P<participation_id>\d+)/beneficiary/(?P<state>\w+)/o/(?P<club_id>\d+)$',
        'challenge_accept_beneficiary_set_donation',
        {'club_class': Club, 'SSL': determine_ssl()}),

    url(r'(?P<participation_id>\d+)/beneficiary/(?P<state>\w+)/t/(?P<club_id>\d+)$',
        'challenge_accept_beneficiary_set_donation',
        {'club_class': TempClub, 'SSL': determine_ssl()}),

    url(r'(?P<participation_id>\d+)/beneficiary/(?P<state>\w+)/create_club$',
        'challenge_accept_beneficiary_create_club', {'SSL': determine_ssl()}),

    url(r'(?P<participation_id>\d+)/beneficiary/(?P<state>\w+)$',
        'challenge_accept_beneficiary', {'SSL': determine_ssl()}),

    url(r'(?P<participation_id>\d+)/state$',
        'challenge_accept_state', {'SSL': determine_ssl()}),

    url(r'challenge_challenge/(?P<participation_id>\d+)/upload$',
        'challenge_challenge_accept_notice', {'SSL': determine_ssl()}),

    url(r'challenge_challenge/beneficiary/(?P<state>\w+)/clubs/o/(?P<club_id>\d+)$',
        'challenge_challenge_accept_notice',
        {'club_entity_type': EntityController.ENTITY_CLUB, 'SSL': determine_ssl()}),

    url(r'challenge_challenge/beneficiary/(?P<state>\w+)/clubs/t/(?P<club_id>\d+)$',
        'challenge_challenge_accept_notice',
        {'club_entity_type': EntityController.ENTITY_TEMP_CLUB, 'SSL': determine_ssl()}),

    url(r'challenge_challenge/beneficiary/(?P<state>\w+)/clubs/create_club$',
        'challenge_challenge_accept_beneficiary_create_club', {'SSL': determine_ssl()}),
    
    url(r'challenge_challenge/beneficiary/(?P<state>\w+)/clubs$',
        'challenge_challenge_accept_beneficiary_load_clubs', {'SSL': determine_ssl()}),

    url(r'challenge_challenge/beneficiary/(?P<state>\w*)$',
        'challenge_challenge_accept_beneficiary', {'SSL': determine_ssl()}),

    url(r'challenge_challenge/(?P<participation_id>\d+)/thanks$',
        'challenge_challenge_thanks', {'SSL': determine_ssl()}),

    url(r'challenge_challenge$',
        'challenge_challenge', {'SSL': determine_ssl()}),

    url(r'(?P<challenge_id>\d+)/accept/notice$',
        'challenge_accept_notice', {'SSL': determine_ssl()}),

    url(r'(?P<challenge_id>\d+)/accept/pay$',
        'challenge_accept_pay', {'SSL': determine_ssl()}),

    url(r'(?P<challenge_id>\d+)/accept/pledge$',
        'challenge_accept_pledge', {'SSL': determine_ssl()}),

    url(r'(?P<challenge_id>\d+)/accept$',
        'challenge_accept_upload', {'SSL': determine_ssl()}),

    url(r'(?P<challenge_id>\d+)/share$',
        'challenge_share', {'SSL': determine_ssl()}),

    url(r'(?P<challenge_id>\d+)/edit_donation$',
        'edit_donation', {'SSL': determine_ssl()}),

    url(r'(?P<challenge_id>\d+)/edit_image$',
        'edit_image', {'SSL': determine_ssl()}),

    url(r'(?P<challenge_id>\d+)$',
        'the_challenge_page', {'SSL': determine_ssl()}),

    url(r'^tick',
        'tick'),
    
    url(r'^send_challenge_emails', 
        'send_challenge_emails'),

    url(r'$',
        'challenges_splash', {'SSL': determine_ssl()}),
)

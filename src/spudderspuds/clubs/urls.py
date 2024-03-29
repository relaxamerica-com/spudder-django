from django.conf.urls.defaults import *
from spudmart.utils.url import determine_ssl

urlpatterns = patterns('spudderspuds.clubs.views',
    # (r'^$', 'splash'),
    #
    # (r'register$', 'register', {'SSL': determine_ssl()}),
    # (r'register/recipient$', 'register_as_recipient', {'SSL': determine_ssl()}),
    # (r'register/recipient/complete$', 'register_as_recipient_complete'),
    # (r'register/recipient/error$', 'register_as_recipient_error'),
    # (r'register/recipient/verification_pending$', 'register_as_recipient_pending_verification'),
    # (r'register/profile', 'register_profile_info'),
    #
    # (r'^signin$', 'signin', {'SSL': determine_ssl()}),
    #
    (r'^dashboard/stripe-connect$', 'dashboard_stripe_connect'),
    (r'^dashboard/edit$', 'dashboard_edit'),
    (r'^dashboard$', 'dashboard'),
    (r'^stripe$', 'stripe', {'SSL': determine_ssl()}),

    # (r'^profile$', 'profile'),
    # (r'^show$', 'show_profile'),
    # (r'^hide$', 'hide_profile'),
    #
    (r'^(?P<club_id>\d+)$', 'public_page'),
    # (r'^(?P<club_id>\d+)/donate$', 'donate'),
    # (r'^not_found$', 'not_found'),
    # (r'^send_message/(?P<club_id>\d+)$', 'send_message'),
    #
    # (r'^edit_cover$', 'edit_cover'),
    # (r'^save_cover$', 'save_cover'),
    # (r'^reset_cover$', 'reset_cover'),
    # (r'^save_thumbnail$', 'save_thumbnail'),
    #
)


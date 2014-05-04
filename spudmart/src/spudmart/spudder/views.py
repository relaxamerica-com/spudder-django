import logging
from django.shortcuts import render_to_response

from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404
from spudmart.donations.models import Donation
from spudmart.spudder.exceptions import SpudderAPIError
from spudmart.spudder.sponsorship import create_or_update_sponsored_teams, create_or_update_team_sponsors, \
    create_or_update_team_offer_sponsors, decrement_team_offer_available_quantity
from spudmart.spudder.users import signup_user, get_user_data, sign_in_user, set_user_is_sponsor
import logging


def synchronise_sponsorship_data_from_donation(_, donation_id):
    logging.error('Synchronizing sponsorhip data: %s' % donation_id)

    donation = get_object_or_404(Donation, pk=donation_id)
    sponsor = donation.donor
    offer = donation.offer
    team = offer.team
    donor_profile = sponsor.get_profile()
    user_spudder_data = None

    try:
        if not donor_profile.spudder_id:
            user_spudder_data = get_user_data(sponsor)
            if not user_spudder_data:
                donor_spudder_id = signup_user(sponsor)
            else:
                donor_spudder_id = user_spudder_data['objectId']

            donor_profile.spudder_id = donor_spudder_id
            donor_profile.save()

        if not user_spudder_data:
            user_spudder_data = get_user_data(sponsor)

        session_token = sign_in_user(user_spudder_data)
        set_user_is_sponsor(donor_profile.spudder_id, session_token)

        create_or_update_sponsored_teams(sponsor, team)
        create_or_update_team_sponsors(team, sponsor)
        create_or_update_team_offer_sponsors(team, offer, sponsor)
        decrement_team_offer_available_quantity(offer)
    except SpudderAPIError, e:
        logging.error('Sponsorship data synchronization error: %s' % e.code)
        logging.error('Donation ID: %s' % donation_id)
        logging.error(e)

        return HttpResponseServerError()
    return HttpResponse()
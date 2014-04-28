from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from spudmart.donations.models import Donation
from spudmart.spudder.sponsorship import create_or_update_sponsored_teams, create_or_update_team_sponsors, \
    create_or_update_team_offer_sponsors
from spudmart.spudder.users import signup_user, get_user_data, sign_in_user, set_user_is_sponsor


def synchronise_sponsorship_data_from_donation(_, donation_id):
    donation = get_object_or_404(Donation, pk=donation_id)

    sponsor = donation.donor
    donor_profile = sponsor.get_profile()
    user_spudder_data = None
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

    team = donation.offer.team
    create_or_update_sponsored_teams(sponsor, team)
    create_or_update_team_sponsors(team, sponsor)
    create_or_update_team_offer_sponsors(team, donation.offer, sponsor)

    return HttpResponse()
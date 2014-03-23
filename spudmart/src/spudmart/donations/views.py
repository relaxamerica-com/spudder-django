from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
import settings
from spudmart.donations.models import Donation, DonationState
from spudmart.utils.amazon import _get_fps_connection, get_donation_cbui_url
from spudmart.spudder.api import get_offer


@login_required
def index(request, offer_id):
    offer = get_offer(offer_id)
    donation = Donation(
        offer=offer,
        donor=request.user,
        donation=offer.donation
    )
    donation.save()

    return render_to_response('dashboard/donations/index.html', {
        'offer': offer,
        'cbui_url': get_donation_cbui_url(donation),
        'spudder_url': '%s/dashboard/teams' % settings.SPUDDER_BASE_URL
    })


def complete(request, donation_id):
    donation = get_object_or_404(Donation, pk=donation_id)
    donation.sender_token_id = request.GET.get('tokenID')
    donation.state = DonationState.PENDING
    donation.save()

    from logging import error
    error(request.get_full_path())

    return HttpResponseRedirect('/dashboard/donation/%s/thanks' % donation_id)


def thanks(request, donation_id):
    donation = get_object_or_404(Donation, pk=donation_id)

    url = '%s//teams/%s/offers/%s' % (
        settings.SPUDDER_BASE_URL,
        donation.offer.team.spudder_id,
        donation.offer.spudder_id)

    return render_to_response('dashboard/donations/thanks.html', {
        'spudder_url': url
    })
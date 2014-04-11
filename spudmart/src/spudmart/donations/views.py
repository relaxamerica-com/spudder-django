from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
import settings
from spudmart.donations.models import Donation, DonationState
from spudmart.spudder.api import get_offer
from spudmart.recipients.models import Recipient
from spudmart.amazon.utils import get_donation_cbui_url, get_fps_connection
from spudmart.amazon.models import AmazonActionStatus


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
    donation.status_code = AmazonActionStatus.get_from_code(request.GET.get('status'))
    
    if donation.status_code is AmazonActionStatus.SUCCESS:
        team = donation.offer.team
        recipients = Recipient.objects.filter(team=team)
        recipientTokenId = recipients[0].recipient_token_id
        
        try:
            connection = get_fps_connection()
            transactionAmount = donation.offer.donation
            connection.pay(RecipientTokenId=recipientTokenId, TransactionAmount=transactionAmount,
                           SenderTokenId=request.GET.get('tokenID'), ChargeFeeTo='Caller',
                           MarketplaceVariableFee='5')
            
            donation.sender_token_id = request.GET.get('tokenID')
            state = DonationState.PENDING
            redirect_to = '/dashboard/donation/%s/thanks' % donation_id
        except Exception, e:
            state = DonationState.TERMINATED
            donation.status_code = AmazonActionStatus.SE
            donation.error_message = e
            redirect_to = '/dashboard/donation/%s/error' % donation_id
    else:
        state = DonationState.TERMINATED
        donation.error_message = request.GET.get('errorMessage', '')
        redirect_to = '/dashboard/donation/%s/error' % donation_id

    donation.state = state
    donation.save()

    return HttpResponseRedirect(redirect_to)


def thanks(request, donation_id):
    donation = get_object_or_404(Donation, pk=donation_id)

    url = '%s//teams/%s/offers/%s' % (
        settings.SPUDDER_BASE_URL,
        donation.offer.team.spudder_id,
        donation.offer.spudder_id)

    return render_to_response('dashboard/donations/thanks.html', {
        'spudder_url': url
    })
    

def error(request, donation_id):
    donation = get_object_or_404(Donation, pk=donation_id)
    status_message = AmazonActionStatus.get_status_message(donation.status_code)
    offer_id = donation.offer.spudder_id
    team_id = donation.offer.team.spudder_id

    return render_to_response('dashboard/donations/error.html', {
        'spudder_url': '%s/teams/%s/offers/%s' % (settings.SPUDDER_BASE_URL, team_id, offer_id),
        'status': status_message,
        'error_message': donation.error_message
    })
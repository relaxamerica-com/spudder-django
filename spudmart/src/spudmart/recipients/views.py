from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
import settings
from spudmart.recipients.models import RecipientRegistrationState
from spudmart.recipients.utils import get_or_create_recipient
from spudmart.spudder.api import get_team, save_team_is_recipient
from spudmart.amazon.models import AmazonActionStatus
from spudmart.amazon.utils import get_recipient_cbui_url

@login_required
def index(request, team_id):
    team = get_team(team_id)
    get_or_create_recipient(team, request.user)

    return render_to_response('dashboard/recipients/index.html', {
        'team': team,
        'cbui_url': get_recipient_cbui_url(team_id),
        'spudder_url': '%s/dashboard/teams' % settings.SPUDDER_BASE_URL
    })


def complete(request, team_id):
    team = get_team(team_id)
    recipient = get_or_create_recipient(team, request.user)
    recipient.status_code = AmazonActionStatus.get_from_code(request.GET.get('status'))

    if recipient.status_code is AmazonActionStatus.SUCCESS:
        result = save_team_is_recipient(team_id)

        if not result:
            state = RecipientRegistrationState.TERMINATED
            recipient.status_code = AmazonActionStatus.SPUDDER_SAVE_FAILED
            redirect_to = '/dashboard/recipient/%s/error' % team_id
        else:
            state = RecipientRegistrationState.FINISHED
            recipient.recipient_token_id=request.GET.get('tokenID')
            recipient.refund_token_id=request.GET.get('refundTokenID')
            redirect_to = '/dashboard/recipient/%s/thanks' % team_id
    else:
        state = RecipientRegistrationState.TERMINATED
        redirect_to = '/dashboard/recipient/%s/error' % team_id

    recipient.state = state
    recipient.save()

    return HttpResponseRedirect(redirect_to)


def thanks(request, team_id):
    return render_to_response('dashboard/recipients/thanks.html', {
        'spudder_url': '%s/dashboard/teams/%s/offers' % (settings.SPUDDER_BASE_URL, team_id)
    })


def error(request, team_id):
    team = get_team(team_id)
    recipient = get_or_create_recipient(team, request.user)
    status_message = AmazonActionStatus.get_status_message(recipient.status_code)

    return render_to_response('dashboard/recipients/error.html', {
        'spudder_url': '%s/dashboard/teams/%s/offers' % (settings.SPUDDER_BASE_URL, team_id),
        'status': status_message
    })
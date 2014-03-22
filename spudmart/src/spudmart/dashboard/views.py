from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import settings
from spudmart.dashboard.models import RecipientRegistration, RecipientRegistrationState, Recipient, \
    RecipientRegistrationStatus
from spudmart.utils.amazon import _get_fps_connection
from spudmart.utils.spudder import get_team_info, save_team_recipient


@login_required
def index(request):
    return render(request, 'dashboard/index.html')


@login_required
def recipient(request, team_id):
    team_info = get_team_info(team_id)
    registrations = RecipientRegistration.objects.filter(team_id=team_id)
    if len(registrations) > 1:
        raise Http404

    if len(registrations) == 0:
        recipient_registration = RecipientRegistration(
            team_id=team_id,
            team_name=team_info['name']
        )
    else:
        recipient_registration = registrations[0]
        recipient_registration.team_id = team_id
        recipient_registration.team_name = team_info['name']

    recipient_registration.save()

    fps_connection = _get_fps_connection()
    cbui_url = fps_connection.cbui_url(returnURL='%s/dashboard/recipient/%s/complete' % (settings.SPUDMART_BASE_URL, team_id),
                                       pipelineName='Recipient',
                                       recipientPaysFee=True)

    return render_to_response('dashboard/recipients/index.html', {
        'team_id': team_id,
        'team_name': team_info['name'],
        'cbui_url': cbui_url,
        'spudder_url': '%s/dashboard/teams' % settings.SPUDDER_BASE_URL
    })


def recipient_complete(request, team_id):
    registrations = RecipientRegistration.objects.filter(team_id=team_id)
    if len(registrations) > 1:
        raise Http404

    registration = registrations[0]
    registration.status_code = RecipientRegistrationStatus.get_from_code(request.GET.get('status'))

    if registration.status_code is RecipientRegistrationStatus.SUCCESS:
        result = save_team_recipient(team_id)
        if not result:
            registration.state = RecipientRegistrationState.TERMINATED
            registration.status_code = RecipientRegistrationStatus.SPUDDER_SAVE_FAILED

        state = RecipientRegistrationState.FINISHED

        new_recipient = Recipient(
            team_id=team_id,
            team_name=registration.team_name,
            recipient_token_id=request.GET.get('tokenID'),
            refund_token_id=request.GET.get('refundTokenID')
        )
        new_recipient.save()
        redirect_to = '/dashboard/recipient/%s/thanks' % team_id
    else:
        state = RecipientRegistrationState.TERMINATED
        redirect_to = '/dashboard/recipient/%s/%s/error' % (team_id, registration.id)

    registration.state = state
    registration.save()

    return HttpResponseRedirect(redirect_to)


def recipient_thanks(request, team_id):
    return render_to_response('dashboard/recipients/thanks.html', {
        'spudder_url': '%s/dashboard/teams/%s/offers' % (settings.SPUDDER_BASE_URL, team_id)
    })


def recipient_error(request, team_id):
    registrations = RecipientRegistration.objects.filter(team_id=team_id)
    if len(registrations) > 1:
        raise Http404

    registration = registrations[0]
    status = RecipientRegistrationStatus.get_status_message(registration.status_code)

    return render_to_response('dashboard/recipients/error.html', {
        'spudder_url': '%s/dashboard/teams/%s/offers' % (settings.SPUDDER_BASE_URL, team_id),
        'status': status
    })
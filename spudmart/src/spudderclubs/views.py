from django.http import HttpResponseRedirect
from django.shortcuts import render
from spudderclubs.decorators import club_admin_required, club_not_fully_activated
from spudderdomain.models import ClubRecipient
from spudmart.amazon.models import AmazonActionStatus, RecipientVerificationStatus
from spudmart.amazon.utils import get_club_register_as_recipient_cbui_url, get_recipient_verification_status
from spudmart.recipients.models import RecipientRegistrationState


def splash(request):
    return render(request, 'spudderclubs/pages/splash.html')


def register(request):
    return render(request, 'spudderclubs/pages/registration/register.html')


@club_admin_required
@club_not_fully_activated
def register_as_recipient(request):
    return render(request, 'spudderclubs/pages/registration/register_as_recipient.html', {
        'cbui_url': get_club_register_as_recipient_cbui_url()
    })


@club_admin_required
@club_not_fully_activated
def register_as_recipient_complete(request):
    club = request.current_role.entity.club
    recipient = ClubRecipient(
        club=club,
        registered_by=request.current_role.entity.admin
    )
    recipient.status_code = AmazonActionStatus.get_from_code(request.GET.get('status'))
    recipient.max_fee = 90

    if recipient.status_code is AmazonActionStatus.SUCCESS:
        recipient.recipient_token_id=request.GET.get('tokenID')
        recipient.refund_token_id=request.GET.get('refundTokenID')
        verification_status = get_recipient_verification_status(recipient.recipient_token_id)

        if verification_status == RecipientVerificationStatus.PENDING:
            state = RecipientRegistrationState.VERIFICATION_PENDING
            redirect_to = '/club/register/verification_pending'
        else:
            state = RecipientRegistrationState.FINISHED
            redirect_to = '/club/register/profile'
    else:
        state = RecipientRegistrationState.TERMINATED
        redirect_to = '/club/register/recipient/error'

    recipient.state = state
    recipient.save()

    return HttpResponseRedirect(redirect_to)


@club_admin_required
@club_not_fully_activated
def register_as_recipient_error(request):
    club = request.current_role.entity.club
    recipient = ClubRecipient.objects.get(club=club)

    status_message = AmazonActionStatus.get_status_message(recipient.status_code)

    return render(request, 'spudderclubs/pages/registration/register_error.html', {
        'failure_reason': status_message
    })


@club_admin_required
@club_not_fully_activated
def register_as_recipient_pending_verification(request):
    return render(request, 'spudderclubs/pages/registration/register_pending_verification.html')


@club_admin_required
@club_not_fully_activated
def register_profile_info(request):
    return render(request, 'spudderclubs/pages/registration/register.html')


@club_admin_required
def dashboard(request):
    club = request.current_role.entity.club

    return render(request, 'spudderclubs/pages/dashboard/dashboard.html', {
        'club': club,
        'cbui_url': get_club_register_as_recipient_cbui_url()
    })
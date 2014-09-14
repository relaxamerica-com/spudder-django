from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from spudderclubs.decorators import club_admin_required, club_not_fully_activated, club_fully_activated
from spudderclubs.forms import ClubProfileCreateForm, ClubProfileEditForm
from spudderdomain.models import ClubRecipient
from spudderspuds.forms import LinkedInSocialMediaForm
from spudderspuds.utils import set_social_media
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
    club = request.current_role.entity.club
    form = ClubProfileCreateForm()
    social_media_form = LinkedInSocialMediaForm()

    if request.method == "POST":
        form = ClubProfileCreateForm(request.POST)
        social_media_form = LinkedInSocialMediaForm(request.POST)

        if form.is_valid() and social_media_form.is_valid():
            club.address = request.POST.get('address')

            location_info = request.POST.get('location_info', None)
            club.update_location(location_info)

            set_social_media(club, social_media_form)

            club.save()

            return redirect('/club/dashboard')

    return render(request, 'spudderclubs/pages/registration/register_profile.html', {
        'form': form,
        'social_media': social_media_form
    })


def signin(request):
    return render(request, 'spudderclubs/pages/registration/signin.html')


@club_admin_required
def dashboard(request):
    club = request.current_role.entity.club

    return render(request, 'spudderclubs/pages/dashboard/dashboard.html', {
        'club': club,
        'cbui_url': get_club_register_as_recipient_cbui_url()
    })


@club_admin_required
@club_fully_activated
def profile(request):
    club = request.current_role.entity.club
    form = ClubProfileEditForm(initial=club.__dict__)
    social_media_form = LinkedInSocialMediaForm(initial=club.__dict__)

    if request.method == "POST":
        form = ClubProfileEditForm(request.POST)
        social_media_form = LinkedInSocialMediaForm(request.POST)

        if form.is_valid() and social_media_form.is_valid():
            club.address = request.POST.get('address')
            club.description = request.POST.get('description')

            location_info = request.POST.get('location_info', None)
            club.update_location(location_info)

            set_social_media(club, social_media_form)

            club.save()

            return redirect('/club/profile')

    return render(request, 'spudderclubs/pages/dashboard/profile.html', {
        'profile': club,
        'form': form,
        'social_media': social_media_form
    })
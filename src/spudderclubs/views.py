from google.appengine.api import mail
import re
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
import settings
from spudderaccounts.wrappers import RoleBase
from spudderclubs.decorators import club_admin_required, club_not_fully_activated, club_fully_activated
from spudderclubs.forms import ClubProfileCreateForm, ClubProfileEditForm
from spudderdomain.controllers import RoleController
from spudderdomain.models import ClubRecipient, Club, ClubAdministrator
from spudderspuds.forms import LinkedInSocialMediaForm
from spudderspuds.utils import set_social_media
from spudmart.amazon.models import AmazonActionStatus, RecipientVerificationStatus
from spudmart.amazon.utils import get_club_register_as_recipient_cbui_url, get_recipient_verification_status
from spudmart.recipients.models import RecipientRegistrationState
from spudmart.upload.models import UploadedFile
from spudmart.utils.cover_image import save_cover_image_from_request, reset_cover_image


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


def public_page(request, club_id):
    club = get_object_or_404(Club, pk=club_id)

    if not club.is_fully_activated():
        raise Http404

    return render(request, 'spudderclubs/pages/public/view.html', {
        'base_url': 'spudderspuds/base.html',
        'profile': club
    })


@club_admin_required
def edit_cover(request):
    club = request.current_role.entity.club

    return render(request, 'components/coverimage/edit_cover_image.html', {
        'name': 'Fan Page',
        'return_url': "/club/%s" % club.id,
        'post_url': '/club/save_cover',
        'reset_url': '/club/reset_cover'
    })


@club_admin_required
def save_cover(request):
    club = request.current_role.entity.club
    save_cover_image_from_request(club, request)

    return HttpResponse()


@club_admin_required
def reset_cover(request):
    club = request.current_role.entity.club
    reset_cover_image(club)

    return HttpResponse('OK')


@club_admin_required
def save_thumbnail(request):
    club = request.current_role.entity.club
    request_logo = request.POST.getlist('thumbnail[]')

    if len(request_logo):
        thumbnail_id = request_logo[0].split('/')[3]
        thumbnail = UploadedFile.objects.get(pk=thumbnail_id)
        club.thumbnail = thumbnail
        club.save()

    return HttpResponse('OK')


def send_message(request, club_id):
    """
    Sends a message to the club manager
    :param request: a POST request with message body
    :param team_id: a valid ID of a Club object
    :return: a blank HttpResponse on success
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    club = get_object_or_404(Club, pk=club_id)
    message = request.POST.get('message', '')

    if not message:
        return HttpResponse()

    admin = ClubAdministrator.objects.filter(club=club)[0]
    entity = RoleController.GetRoleForEntityTypeAndID(
        RoleController.ENTITY_CLUB_ADMIN,
        admin.id,
        RoleBase.RoleWrapperByEntityType(RoleController.ENTITY_CLUB_ADMIN)
    )
    email = entity.user.email

    if message:
        to = ['support@spudder.zendesk.com', email]
        mail.send_mail(
            subject='Message from Spudder about Club: %s' % club.name,
            body=message,
            sender=settings.SERVER_EMAIL,
            to=to
        )

    return HttpResponse()
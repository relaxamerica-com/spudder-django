import httplib
import json
import logging
import traceback
import urllib

from google.appengine.api import blobstore

from django.contrib import messages
from django.shortcuts import render, redirect
import settings
from spudderdomain.wrappers import EntityBase
from spudderspuds.clubs.decorators import club_admin_required
from spudderspuds.clubs.forms import ClubProfileBasicDetailsForm
from spudderdomain.controllers import EntityController, EventController
from spudderdomain.models import StripeUser
from spudderspuds.clubs.utils import get_club_and_club_entity
from spudderstripe.controllers import StripeController
from spudderstripe.utils import get_stripe_recipient_controller_for_club
from spudmart.upload.forms import UploadForm


@club_admin_required
def dashboard(request):
    club, club_entity = get_club_and_club_entity(request)
    stripe_controller = get_stripe_recipient_controller_for_club(club)
    if not stripe_controller:
        if EventController.PopEvent(request, EventController.CLUB_REGISTERED):
            messages.success(
                request,
                "You are almost finished registering %s, just one more step to go." % club_entity.name)
        return redirect('/club/dashboard/stripe-connect')
    template_data = {
        'stripe': stripe_controller,
        'club_entity': club_entity}
    return render(request, 'spudderspuds/clubs/pages/dashboard.html', template_data)


@club_admin_required
def dashboard_stripe_connect(request):
    club, club_entity = get_club_and_club_entity(request)
    template_data = {'club_entity': club_entity}
    return render(request, 'spudderspuds/clubs/pages/dashboard_stripe_connect.html', template_data)


@club_admin_required
def dashboard_edit(request):
    club = request.current_role.entity.club
    club_entity = EntityController.GetWrappedEntityByTypeAndId(
        EntityController.ENTITY_CLUB,
        club.id,
        EntityBase.EntityWrapperByEntityType(EntityController.ENTITY_CLUB))
    basic_details_form = ClubProfileBasicDetailsForm(club=club, initial=club.__dict__)
    if request.method == 'POST':
        if request.FILES:
            icon = UploadForm(request.POST, request.FILES).save()
            club.thumbnail = icon
            club.save()
        basic_details_form = ClubProfileBasicDetailsForm(club=club, data=request.POST)
        if basic_details_form.is_valid():
            for attr in ('name', ):
                setattr(club, attr, basic_details_form.cleaned_data.get(attr))
            club.save()
            messages.success(request, 'Team details updated.')
    template_data = {
        'upload_url': blobstore.create_upload_url('/club/dashboard/edit'),
        'club_entity': club_entity,
        'basic_details_form': basic_details_form}
    return render(request, 'spudderspuds/clubs/pages/dashboard_edit.html', template_data)


@club_admin_required
def stripe(request):
    exception_occurred = False
    club, club_entity = get_club_and_club_entity(request)
    message = None
    json_data = None
    try:
        code = request.GET.get('code', '')
        params = urllib.urlencode({
            'client_secret': settings.STRIPE_SECRET_KEY,
            'code': code,
            'grant_type': 'authorization_code'})
        url = '/oauth/token?%s' % params
        connection = httplib.HTTPSConnection('connect.stripe.com')
        connection.connect()
        connection.request('POST', url)
        resp = connection.getresponse()
        resp_data = resp.read()
        json_data = json.loads(resp_data)
        stripe_user = StripeUser(
            club=club,
            code=code,
            access_token=json_data['access_token'],
            refresh_token=json_data['refresh_token'],
            publishable_key=json_data['stripe_publishable_key'],
            user_id=json_data['stripe_user_id'],
            scope=json_data['scope'],
            token_type=json_data['token_type'])
        stripe_user.save()
        stripe_controller = StripeController(stripe_user)
        account_details = stripe_controller.get_account_details()
        if not account_details or not account_details.get('display_name'):
            message = 'It looks like you registered with Stripe but did not provide a valid business name for your ' \
                      'organization. Please contact support@spudder.com quoting "NO STRIPE NAME".'
            raise Exception
        club_display_name = account_details['display_name']
        club.name = club_display_name
        club.name_is_fixed = True
        club.save()
        messages.success(
            request,
            "Congratulations, you have successfully connected with Stripe and can now start fundraising on Spudder. "
            "Your organizations name has been changed to match the IRS records you provided to Stripe and is now set "
            "to '%s'." % club_display_name)
    except httplib.HTTPException:
        exception_occurred = True
        logging.error('Http connection exception while trying to contact Stripe API server')
    except KeyError:
        exception_occurred = True
        logging.error('Access token missing in JSON object. Probably Stripe keys are configured improperly')
        logging.error(json_data)
    except Exception as e:
        exception_occurred = True

    if exception_occurred:
        logging.error(traceback.format_exc())
        try:
            StripeUser.objects.get(club=club).delete()
        except StripeUser.DoesNotExist:
            pass
        if not message:
            message = "Sorry, there was an error connecting your stripe account. Please try again and contact " \
                      "support@spudder.com if the problem continues."
        messages.error(
            request,
            message)
    return redirect('/club/dashboard')

    # def splash(request):
    #     return render(request, 'spudderspuds/clubs/_old/pages/splash.html')
    #
    #
    # def register(request):
    #     return render(request, 'spudderspuds/clubs/_old/registration/register.html')
    #
    #
    # @club_admin_required
    # @club_not_fully_activated
    # def register_as_recipient(request):
    #     return render(request, 'spudderspuds/clubs/_old/registration/register_as_recipient.html', {
    #         'cbui_url': get_club_register_as_recipient_cbui_url()
    #     })
    #
    #
    # @club_admin_required
    # @club_not_fully_activated
    # def register_as_recipient_complete(request):
    #     club = request.current_role.entity.club
    #     recipient = ClubRecipient(
    #         club=club,
    #         registered_by=request.current_role.entity.admin
    #     )
    #     recipient.status_code = AmazonActionStatus.get_from_code(request.GET.get('status'))
    #     recipient.max_fee = 90
    #
    #     if recipient.status_code is AmazonActionStatus.SUCCESS:
    #         recipient.recipient_token_id=request.GET.get('tokenID')
    #         recipient.refund_token_id=request.GET.get('refundTokenID')
    #         verification_status = get_recipient_verification_status(recipient.recipient_token_id)
    #
    #         if verification_status == RecipientVerificationStatus.PENDING:
    #             state = RecipientRegistrationState.VERIFICATION_PENDING
    #             redirect_to = '/club/register/verification_pending'
    #         else:
    #             state = RecipientRegistrationState.FINISHED
    #             id = request.session['invitation_id']
    #             if id:
    #                 inv = Invitation.objects.get(id=id)
    #                 inv.status = Invitation.ACCEPTED_STATUS
    #                 inv.save()
    #                 request.session['invitation_id'] = None
    #                 redirect_to = '/spudderaffiliates/invitation/%s/create_team' % id
    #             else:
    #                 redirect_to = '/club/register/profile'
    #     else:
    #         state = RecipientRegistrationState.TERMINATED
    #         redirect_to = '/club/register/recipient/error'
    #
    #     recipient.state = state
    #     recipient.save()
    #
    #     return HttpResponseRedirect(redirect_to)
    #
    #
    # @club_admin_required
    # @club_not_fully_activated
    # def register_as_recipient_error(request):
    #     club = request.current_role.entity.club
    #     recipient = ClubRecipient.objects.get(club=club)
    #
    #     status_message = AmazonActionStatus.get_status_message(recipient.status_code)
    #
    #     return render(request, 'spudderspuds/clubs/_old/registration/register_error.html', {
    #         'failure_reason': status_message
    #     })
    #
    #
    # @club_admin_required
    # @club_not_fully_activated
    # def register_as_recipient_pending_verification(request):
    #     return render(request, 'spudderspuds/clubs/_old/registration/register_pending_verification.html')
    #
    #
    # @club_admin_required
    # @club_not_fully_activated
    # def register_profile_info(request):
    #     club = request.current_role.entity.club
    #     form = ClubProfileCreateForm()
    #     social_media_form = LinkedInSocialMediaForm()
    #     if request.method == "POST":
    #         form = ClubProfileCreateForm(request.POST)
    #         social_media_form = LinkedInSocialMediaForm(request.POST)
    #         if form.is_valid() and social_media_form.is_valid():
    #             club.address = request.POST.get('address')
    #             club.state = form.cleaned_data.get('state')
    #             location_info = request.POST.get('location_info', None)
    #             club.update_location(location_info)
    #             set_social_media(club, social_media_form)
    #             club.save()
    #             return redirect('/club/dashboard')
    #     return render(request, 'spudderspuds/clubs/_old/registration/register_profile.html', {
    #         'form': form,
    #         'social_media': social_media_form
    #     })
    #
    #
    #
    #
    # def signin(request):
    #     return render(request, 'spudderspuds/clubs/_old/registration/signin.html')
    #
    #
    # @club_admin_required
    # @club_fully_activated
    # def profile(request):
    #     club = request.current_role.entity.club
    #     form = ClubProfileEditForm(initial=club.__dict__)
    #     social_media_form = LinkedInSocialMediaForm(initial=club.__dict__)
    #
    #     if request.method == "POST":
    #         form = ClubProfileEditForm(request.POST)
    #         social_media_form = LinkedInSocialMediaForm(request.POST)
    #
    #         if form.is_valid() and social_media_form.is_valid():
    #             club.address = request.POST.get('address')
    #             club.description = request.POST.get('description')
    #
    #             location_info = request.POST.get('location_info', None)
    #             club.update_location(location_info)
    #
    #             set_social_media(club, social_media_form)
    #
    #             club.save()
    #
    #             return redirect('/club/profile')
    #
    #     return render(request, 'spudderspuds/clubs/_old/dashboard/profile.html', {
    #         'profile': club,
    #         'form': form,
    #         'social_media': social_media_form
    #     })
    #
    #
    # @club_admin_required
    # @club_fully_activated
    # def hide_profile(request):
    #     club = request.current_role.entity.club
    #
    #     if request.method == "POST":
    #         club.hidden = True
    #         club.save()
    #
    #         return redirect('/club/dashboard')
    #
    #     return render(request, 'spudderspuds/clubs/_old/dashboard/hide_profile.html', {
    #         'profile': club
    #     })
    #
    #
    # @club_admin_required
    # @club_fully_activated
    # def show_profile(request):
    #     club = request.current_role.entity.club
    #
    #     if request.method == "POST":
    #         club.hidden = False
    #         club.save()
    #
    #         return redirect('/club/dashboard')
    #
    #     return render(request, 'spudderspuds/clubs/_old/dashboard/show_profile.html', {
    #         'profile': club
    #     })
    #
    #
    # def public_page(request, club_id):
    #     club = get_object_or_none(Club, pk=club_id)
    #
    #     if not club or not club.is_fully_activated or club.is_hidden():
    #         return HttpResponseRedirect('/club/not_found')
    #
    #     team_ids = list(TeamClubAssociation.objects.filter(club=club).values_list('team_page', flat=True))
    #     teams = TeamPage.objects.filter(id__in=team_ids)
    #     return render(request, 'spudderspuds/clubs/_old/public/view.html', {
    #         'base_url': 'spudderspuds/base.html',
    #         'profile': club,
    #         'teams': teams,
    #         'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    #     })
    #
    #
    # def donate(request, club_id):
    #     club = get_object_or_none(Club, pk=club_id)
    #
    #     if not club or not club.is_fully_activated or club.is_hidden():
    #         return HttpResponseRedirect('/club/not_found')
    #
    #     stripe_token = request.POST.get('stripeToken')
    #     stripe_user = StripeUser.objects.get(club=club)
    #
    #     import stripe
    #     stripe.api_key = settings.STRIPE_CLIENT_ID
    #
    #     stripe.Charge.create(
    #         amount=2000,
    #         currency="usd",
    #         card=stripe_token,  # obtained with Stripe.js
    #         description="Simple donation for %s club" % club.name,
    #         application_fee=123, # amount incents
    #         api_key=stripe_user.access_token # user's access token from the Stripe Connect flow
    #     )
    #
    #     return HttpResponseRedirect('/club/%s' % club_id)
    #
    #
    # def not_found(request):
    #     clubs = Club.objects.filter(hidden=False)[:5]
    #
    #     return render(request, 'spudderspuds/clubs/_old/public/not_found.html', {
    #         'clubs': clubs
    #     })
    #
    #
    # @club_admin_required
    # def edit_cover(request):
    #     club = request.current_role.entity.club
    #
    #     return render(request, 'components/coverimage/edit_cover_image.html', {
    #         'name': 'Fan Page',
    #         'return_url': "/club/%s" % club.id,
    #         'post_url': '/club/save_cover',
    #         'reset_url': '/club/reset_cover'
    #     })
    #
    #
    # @club_admin_required
    # def save_cover(request):
    #     club = request.current_role.entity.club
    #     save_cover_image_from_request(club, request)
    #
    #     return HttpResponse()
    #
    #
    # @club_admin_required
    # def reset_cover(request):
    #     club = request.current_role.entity.club
    #     reset_cover_image(club)
    #
    #     return HttpResponse('OK')
    #
    #
    # @club_admin_required
    # def save_thumbnail(request):
    #     club = request.current_role.entity.club
    #     request_logo = request.POST.getlist('thumbnail[]')
    #
    #     if len(request_logo):
    #         thumbnail_id = request_logo[0].split('/')[3]
    #         thumbnail = UploadedFile.objects.get(pk=thumbnail_id)
    #         club.thumbnail = thumbnail
    #         club.save()
    #
    #     return HttpResponse('OK')
    #
    #
    # def send_message(request, club_id):
    #     """
    #     Sends a message to the club manager
    #     :param request: a POST request with message body
    #     :param team_id: a valid ID of a Club object
    #     :return: a blank HttpResponse on success
    #     """
    #     if request.method != 'POST':
    #         return HttpResponseNotAllowed(['POST'])
    #
    #     club = get_object_or_404(Club, pk=club_id)
    #     message = request.POST.get('message', '')
    #
    #     if not message:
    #         return HttpResponse()
    #
    #     admin = ClubAdministrator.objects.filter(club=club)[0]
    #     entity = RoleController.GetRoleForEntityTypeAndID(
    #         RoleController.ENTITY_CLUB_ADMIN,
    #         admin.id,
    #         RoleBase.RoleWrapperByEntityType(RoleController.ENTITY_CLUB_ADMIN)
    #     )
    #     email = entity.user.email
    #
    #     if message:
    #         to = ['support@spudder.zendesk.com', email]
    #         mail.send_mail(
    #             subject='Message from Spudder about Club: %s' % club.name,
    #             body=message,
    #             sender=settings.SERVER_EMAIL,
    #             to=to
    #         )
    #
    #     return HttpResponse()
    #
    #
    # @club_admin_required
    # def stripe(request):
    #     club = request.current_role.entity.club
    #
    #     params = urllib.urlencode({
    #         'client_secret': settings.STRIPE_SECRET_KEY,
    #         'code': request.GET.get('code', ''),
    #         'grant_type': 'authorization_code'
    #     })
    #     url = '/oauth/token?%s' % params
    #
    #     connection = httplib.HTTPSConnection('connect.stripe.com')
    #     connection.connect()
    #     connection.request('POST', url)
    #
    #     resp = connection.getresponse()
    #     resp_data = resp.read()
    #
    #     json_data = json.loads(resp_data)
    #
    #     StripeUser(
    #         club=club,
    #         access_token=json_data['access_token'],
    #         refresh_token=json_data['refresh_token'],
    #         publishable_key=json_data['stripe_publishable_key'],
    #         user_id=json_data['stripe_user_id'],
    #         scope=json_data['scope'],
    #         token_type=json_data['token_type'],
    #     ).save()
    #
    #
    #     return HttpResponseRedirect('/club/dashboard')
import json
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from spudderdomain.models import TeamVenueAssociation
from spudmart.utils.cover_image import reset_cover_image, save_cover_image_from_request
from spudmart.utils.emails import send_email
from spudmart.venues.models import Venue, SPORTS, PendingVenueRental
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed
from spudmart.upload.models import UploadedFile
import simplejson
from spudmart.recipients.models import VenueRecipient,\
    RecipientRegistrationState
from spudmart.amazon.utils import get_venue_recipient_cbui_url,\
    get_rent_venue_cbui_url, get_fps_connection, get_rent_venue_ipn_url, parse_ipn_notification_request
from spudmart.amazon.models import AmazonActionStatus, IPNTransactionStatus
import settings
from spudmart.donations.models import RentVenue, DonationState
from google.appengine.api import mail
from django.contrib.auth.decorators import login_required
from spudmart.sponsors.models import SponsorPage
from spudmart.accounts.utils import is_sponsor
from spudmart.CERN.rep import added_basic_info, added_photos, added_logo, \
                            added_video
from spudmart.CERN.models import Student

from spudderdomain.controllers import SpudsController, RoleController
from spudderkrowdio.models import KrowdIOStorage
from spudderkrowdio.utils import get_user_mentions_activity, delete_spud
import logging
import datetime


def view(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)

    if request.method == "POST":
        venue.name = request.POST.get('name', '')
        venue.aka_name = request.POST.get('aka_name', '')
        venue.save()

    role = request.current_role

    splitted_address = venue.medical_address.split(', ')
    medical_address = {
        'address': splitted_address.pop(0) if splitted_address else '',
        'city': splitted_address.pop(0) if splitted_address else '',
        'state': splitted_address.pop(0) if splitted_address else '',
        'zip': splitted_address.pop(0) if splitted_address else ''
    }

    try:
        student = Student.objects.get(id=role.entity.id)
    except Student.DoesNotExist:
        student = False
    except TypeError:
        student = False
    except AttributeError:
        student = False

    is_recipient = VenueRecipient.objects.filter(groundskeeper=student)
    rent_venue_url = False
    can_edit = request.user.is_authenticated() and (venue.is_groundskeeper(role) or venue.is_renter(role))
    if venue.is_available() and not venue.is_renter(role):
        rent_venue_url = get_rent_venue_cbui_url(venue)

    sponsor = venue.renter
    sponsor_info = False
    if sponsor:
        if sponsor.name != "":
            sponsor_info = True
    
    storage = KrowdIOStorage.GetOrCreateForVenue(venue_id)
    venue_spuds = get_user_mentions_activity(storage)
    teams = [team.team_page for team in TeamVenueAssociation.objects.filter(venue=venue)]

    return render(request, 'spuddercern/pages/venues_view.html', {
        'venue': venue,
        'teams': teams,
        'sports': SPORTS,
        'medical_address': medical_address,
        'is_recipient': is_recipient,
        'rent_venue_url': rent_venue_url,
        'sponsor': sponsor,
        'sponsor_info': sponsor_info,
        'is_sponsor': venue.is_renter(role),
        'student': student,
        'venue_spuds': venue_spuds,
        'base_url': 'spuddercern/base.html',
    })

def index(request):
    return render(request, 'spuddercern/pages/venue_index.html')

@login_required
def list_view(request):
    if is_sponsor(request.user):
        sponsor_page = SponsorPage.objects.get(sponsor=request.user)
        venues = Venue.objects.filter(sponsor=sponsor_page)
        template = 'spuddercern/sponsor_dashboard/venues.html'
    else:
        venues = Venue.objects.filter(user=request.user)
        template = 'venues/list.html'

    return render(request, template, {'venues': venues})

# VENUE ENDPOINTS

def save_coordinates(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue.latitude = float(request.POST['latitude'])
    venue.longitude = float(request.POST['longitude'])
    venue.save()
    return HttpResponse('OK')

def save_parking_details(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    parking_pics = request.POST.getlist('parking_pics[]')
    parking_details = request.POST['parking_details']

    # Reward student for completing parking info
    if len(venue.parking_pics) == 0 or venue.parking_details == '':
        if len(parking_pics) and parking_details != '':
            added_basic_info(venue)

    # Add pics and details and save
    venue.parking_pics.extend(parking_pics)
    venue.parking_details = parking_details
    venue.save()
    return HttpResponse('OK')

def save_venue_pics(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue_pics = request.POST.getlist('venue_pics[]')

    # If there were no photos, but now there are, add points
    if len(venue.venue_pics) == 0:
        if len(venue_pics):
            added_photos(venue)

    #Add photos and save
    venue.venue_pics.extend(venue_pics)
    venue.save()
    return HttpResponse('OK')

def save_logo_and_name(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)

    request_logo = request.POST.getlist('logo[]')
    if len(request_logo):
        logo_id = request_logo[0].split('/')[3]
        logo = UploadedFile.objects.get(pk = logo_id)

        # Check if this is the first logo to be added, if so add points
        if not venue.logo:
            added_logo(venue)

        # Update logo
        venue.logo = logo

    # If either name has been customized for the first time, add points
    request_name = request.POST['name']
    request_aka_name = request.POST['aka_name']
    default_name = Venue._meta.get_field('name').default
    default_aka_name = Venue._meta.get_field('aka_name').default
    if venue.name == default_name:
        if request_name != default_name:
            added_basic_info(venue)
    if venue.aka_name == default_aka_name:
        if request_aka_name != default_aka_name:
            added_basic_info(venue)

    # Update name(s)
    venue.name = request_name
    venue.aka_name = request_aka_name
    venue.save()
    return HttpResponse('OK')

def save_playing_surface_pics(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    playing_surface_pics = request.POST.getlist('playing_surface_pics[]')
    playing_surface_details = request.POST['playing_surface_details']

    # Check if pics and details are added, if so add points
    if len(venue.playing_surface_pics) == 0 or venue.playing_surface_details == '':
        if len(playing_surface_pics) and playing_surface_details != '':
            added_basic_info(venue)

    # Add pics and details and save
    venue.playing_surface_pics.extend(playing_surface_pics)
    venue.playing_surface_details = request.POST['playing_surface_details']
    venue.save()
    return HttpResponse('OK')

def save_video(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    video = request.POST['video']

    # If this is the first time a video is added, add points
    if venue.video == '':
        if video:
            added_video(venue)

    # Save video
    venue.video = video
    venue.save()
    return HttpResponse('OK')

def save_restroom_details(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    restroom_details = request.POST['restroom_details']
    restroom_pics = request.POST.getlist('restroom_pics[]')

    # If everything is filled in for the first time, add points
    if venue.restroom_details == '' or len(venue.restroom_pics) == 0:
        if restroom_details and len(restroom_pics):
            added_basic_info(venue)

    # Save restroom details
    venue.restroom_details = restroom_details
    venue.restroom_pics.extend(restroom_pics)
    venue.save()
    return HttpResponse('OK')

def save_concession_details(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    concession_pics = request.POST.getlist('concession_pics[]')
    concession_details = request.POST['concession_details']

    # Reward student for completing concession info
    if len(venue.concession_pics) == 0 or venue.concession_details == '':
        if len(concession_pics) and concession_details != '':
            added_basic_info(venue)

    # Add pics and details and save
    venue.concession_pics.extend(concession_pics)
    venue.concession_details = concession_details
    venue.save()
    return HttpResponse('OK')

def save_admission_details(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    admission_pics = request.POST.getlist('admission_pics[]')
    admission_details = request.POST['admission_details']

    # Reward student for completing admission info
    if len(venue.admission_pics) == 0 or venue.admission_details == '':
        if len(admission_pics) and admission_details != '':
            added_basic_info(venue)

    # Add pics and details and save
    venue.admission_pics.extend(admission_pics)
    venue.admission_details = admission_details
    venue.save()
    return HttpResponse('OK')

# def save_shelter_details(request, venue_id):
#     venue = Venue.objects.get(pk = venue_id)
#     shelter_details = request.POST['shelter_details']
#
#     # If this is filled in for the first time, add points
#     if venue.shelter_details == '':
#         if shelter_details:
#             added_basic_info(venue)
#
#     # Update and save shelter details
#     venue.shelter_details = shelter_details
#     venue.save()
#     return HttpResponse('OK')

def save_medical_details(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    medical_address = request.POST['medical_address']

    # If this is filled in for the first time, add points
    if venue.medical_address == '':
        if medical_address:
            added_basic_info(venue)

    # Update and save medical details
    venue.medical_address = medical_address
    venue.save()
    return HttpResponse('OK')

def save_handicap_details(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    handicap_pics = request.POST.getlist('handicap_pics[]')
    handicap_details = request.POST['handicap_details']

    # Reward student for completing handicap info
    if len(venue.handicap_pics) == 0 or venue.handicap_details == '':
        if len(handicap_pics) and handicap_details != '':
            added_basic_info(venue)

    # Add pics and details and save
    venue.handicap_pics.extend(handicap_pics)
    venue.handicap_details = handicap_details
    venue.save()
    return HttpResponse('OK')

def send_message(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    message = request.POST.get('message', '')
    to = []
    to.append('support@spudder.zendesk.com')
    to.append(venue.student.user.email)
    mail.send_mail(subject='Message from Spudmart about Venue: %s' % venue.name, body=message, sender=settings.SERVER_EMAIL, to=to)

    return HttpResponse('OK')

def save_price(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue.price = float(request.POST['price'])
    venue.save()
    return HttpResponse('OK')

def get_venues_within_bounds(request):
    latitude_range = [float(value) for value in request.GET.getlist('latitude_range[]')]
    longitude_range = [float(value) for value in request.GET.getlist('longitude_range[]')]

    if longitude_range[0] < 0 and longitude_range[1] < 0:
        longitude_range.reverse()

    venues_in_latitude_range = Venue.objects.filter(latitude__range = latitude_range)
    venues_in_longitude_range = Venue.objects.filter(longitude__range = longitude_range)

    venues = []
    for venue in venues_in_latitude_range:
        if venue in venues_in_longitude_range:
            venues.append({
                'id' : venue.id,
                'name' : venue.name,
                'aka_name' : venue.aka_name,
                'latitude' : venue.latitude,
                'longitude' : venue.longitude,
                'sport' : venue.sport
            })

    venues_dict = {
        'venues' : venues
    }

    return HttpResponse(simplejson.dumps(venues_dict))

def fix_venue_coordinates(request):
    for venue in Venue.objects.all():
        splitted = venue.coordinates.split(',')
        venue.latitude = float(splitted[0])
        venue.longitude = float(splitted[1])
        venue.save()
    return HttpResponse('OK')

def remove_pic(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    list_type = request.POST['list_type']
    file_url = request.POST['file_url']

    the_list = getattr(venue, list_type)

    if file_url in the_list:
        the_list.remove(file_url)

    setattr(venue, list_type, the_list)

    venue.save()

    return HttpResponse('OK')

# AMAZON

def recipient(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)

    return render(request, 'spuddercern/pages/recipient_register.html', {
        'cbui_url': get_venue_recipient_cbui_url(venue)
    })


def complete(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue_recipient, _ = VenueRecipient.objects.get_or_create(groundskeeper = venue.student)
    venue_recipient.status_code = AmazonActionStatus.get_from_code(request.GET.get('status'))
    venue_recipient.max_fee = 50

    if venue_recipient.status_code is AmazonActionStatus.SUCCESS:
        state = RecipientRegistrationState.FINISHED
        venue_recipient.recipient_token_id=request.GET.get('tokenID')
        venue_recipient.refund_token_id=request.GET.get('refundTokenID')
        redirect_to = '/venues/recipient/%s/thanks' % venue_id
    else:
        state = RecipientRegistrationState.TERMINATED
        redirect_to = '/venues/recipient/%s/error' % venue_id

    venue_recipient.state = state
    venue_recipient.save()

    return HttpResponseRedirect(redirect_to)


def thanks(request, venue_id):
    return render(request, 'spuddercern/pages/recipient_thanks.html', {
        'spudder_url': '%s/venues/view/%s' % (settings.SPUDMART_BASE_URL, venue_id)
    })


def error(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    recipient = VenueRecipient.objects.get_or_create(groundskeeper = venue.student)
    status_message = AmazonActionStatus.get_status_message(recipient.status_code)

    return render(request, 'spuddercern/pages/recipient_error.html', {
        'spudder_url': '%s/venues/view/%s' % (settings.SPUDMART_BASE_URL, venue_id),
        'status': status_message
    })


def _pending_rental_logic(request, venue):
    pending_rental = PendingVenueRental(venue=venue)
    pending_rental.save()

    try:
        pending_session_venues = request.session['pending_venues_rental']
        pending_session_venues += ',' + str(pending_rental.id)
    except KeyError:
        pending_session_venues = str(pending_rental.id)

    request.session['pending_venues_rental'] = pending_session_venues
    state = DonationState.PENDING
    redirect_to = '/venues/rent_venue/sign_in'

    return redirect_to, state


def rent_complete(request, venue_id):
    venue = get_object_or_404(Venue, pk = venue_id)

    rent_venue, _ = RentVenue.objects.get_or_create(venue=venue)
    rent_venue.status_code = AmazonActionStatus.get_from_code(request.GET.get('status'))

    if rent_venue.status_code is AmazonActionStatus.SUCCESS:
        recipients = VenueRecipient.objects.filter(groundskeeper=venue.student)
        recipient_token_id = recipients[0].recipient_token_id

        try:
            connection = get_fps_connection()
            transaction_amount = venue.price
            venue_ipn_url = get_rent_venue_ipn_url(venue, request.user)

            connection.pay(
                RecipientTokenId=recipient_token_id,
                TransactionAmount=transaction_amount,
                SenderTokenId=request.GET.get('tokenID'),
                ChargeFeeTo='Caller',
                MarketplaceVariableFee='50',
                OverrideIPNURL=venue_ipn_url
            )

            rent_venue.sender_token_id = request.GET.get('tokenID')

            if not request.user.is_authenticated():
                redirect_to, state = _pending_rental_logic(request, venue)
            elif request.current_role.entity_type is not RoleController.ENTITY_SPONSOR:
                # We need to check if currently used role is a Sponsor, because users can rent Venues with different
                # roles but already have the Sposnor role assigned, but not activated
                redirect_to, state = _pending_rental_logic(request, venue)
            else:
                try:
                    state = DonationState.FINISHED
                    sponsor_page = SponsorPage.objects.get(sponsor=request.user)
                    venue.renter = sponsor_page
                    venue.save()
                    redirect_to = '/venues/rent_venue/%s/thanks' % venue.pk
                except SponsorPage.DoesNotExist:
                    # Missing Sponsor page means that in the past something went wrong while finalizing transaction
                    # and Sponsor profile wasn't created. In that case the only way is to create Sponsor profile again.
                    redirect_to, state = _pending_rental_logic(request, venue)
        except Exception, e:
            state = DonationState.TERMINATED
            rent_venue.status_code = AmazonActionStatus.SE
            rent_venue.error_message = e
            redirect_to = '/venues/rent_venue/%s/error' % venue.pk
    else:
        state = DonationState.TERMINATED
        rent_venue.error_message = request.GET.get('errorMessage', '')
        redirect_to = '/venues/rent_venue/%s/error' % venue.pk

    rent_venue.state = state
    rent_venue.save()

    return HttpResponseRedirect(redirect_to)


def _handle_sign_in_complete(request):
    try:
        pending_session_venues = request.session['pending_venues_rental']
    except KeyError:
        # No pending venue rentals in session, move forward
        return HttpResponseRedirect('/')

    # direct import so that testing framework can properly mock function
    from spudmart.venues.utils import finalize_pending_rentals as finalize
    finalize(pending_session_venues, request.current_role)

    del request.session['pending_venues_rental']

    return HttpResponseRedirect('/sponsor/page')


def rent_sign_in(request):
    if request.user.is_authenticated() and request.current_role.entity_type is RoleController.ENTITY_SPONSOR:
        return _handle_sign_in_complete(request)

    return render(request, 'spuddercern/pages/rent_venue_signin.html', {
        'client_id': settings.AMAZON_LOGIN_CLIENT_ID,
        'base_url': settings.SPUDMART_BASE_URL
    })


def rent_sign_in_complete(request):
    return _handle_sign_in_complete(request)


def rent_thanks(request, venue_id):
    return render(request, 'spuddercern/pages/rent_venue_thanks.html', {
        'spudder_url': '%s/sponsor/page' % settings.SPUDMART_BASE_URL,
        'venue_url': '%s/venues/view/%s' % (settings.SPUDMART_BASE_URL, venue_id)
    })


def rent_error(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)
    rent_venue = RentVenue.objects.get(venue=venue)
    status_message = AmazonActionStatus.get_status_message(rent_venue.status_code)

    return render(request, 'spuddercern/pages/rent_venue_error.html', {
        'spudder_url': '%s/venues/view/%s' % (settings.SPUDMART_BASE_URL, venue.id),
        'status': status_message,
        'error_message': rent_venue.error_message
    })


def rent_notification(request, venue_id, user_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])

    user = get_object_or_404(User, pk=user_id)
    venue = get_object_or_404(Venue, pk=venue_id)
    rent_venue = RentVenue.objects.get(venue=venue)

    parsed_status = parse_ipn_notification_request(request)
    parsed_status.transaction_type = 'Venue'
    parsed_status.transaction_entity_id = venue_id
    parsed_status.transaction_user = user
    parsed_status.save()

    if parsed_status.transactionStatus not in [IPNTransactionStatus.SUCCESS, IPNTransactionStatus.PENDING]:  # ERROR
        rent_venue.state = DonationState.TERMINATED
        rent_venue.status_code = AmazonActionStatus.PE
        rent_venue.error_message = parsed_status.statusMessage
        rent_venue.save()

        venue.sponsor = None
        venue.save()

        message_body = render_to_string('spuddercern/pages/rent_venue_rent_error.html', {
            'venue': venue,
            'error_message': rent_venue.error_message,
            'venue_url': '%s/venues/view/%s' % (settings.SPUDMART_BASE_URL, venue.id)
        })

        send_email(settings.SERVER_EMAIL, user.email, 'Venue renting payment error', message_body)

    return HttpResponse('OK')


def delete_venue(request, venue_id):
    """
    Deletes a venue

    :param request: request to delete venue
    :param venue_id: venue to be deleted
    :return: redirect to venues list
    """
    venue = Venue.objects.get(id=venue_id)
    venue.delete()
    return HttpResponseRedirect('/venues/list')


def get_instagram_stream(request, venue_id):
    controller = SpudsController(request.current_role)
    filters = request.GET.get('filter', None)
    results = controller.get_unapproved_spuds(venue_id, filters=filters)
    template_data = {'results': results, 'venue_id': venue_id}
    if filters == "day-0":
        template_data['filter_message'] = "Showing posts from today"
    elif filters == "day-1":
        template_data['filter_message'] = "Showing posts from yesterday"
    elif filters == "day-7":
        template_data['filter_message'] = "Showing older posts"
    elif filters:
        template_data['filter_message'] = "Showing posts from %s days ago" % filters.replace('day-', '')
    return render(
        request,
        'spuddercern/pages/venue_instagram_stream.html',
        template_data)


def accept_spud_from_social_media(request, venue_id, spud_from_social_media_id):
    controller = SpudsController(request.current_role)
    controller.approve_spuds([spud_from_social_media_id], venue_id)
    return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')
        
    
def reject_spud_from_social_media(request, venue_id, spud_from_social_media_id):
    controller = SpudsController(request.current_role)
    controller.reject_spuds([spud_from_social_media_id])
    return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')


def accept_instagram_media(request, venue_id):
    # controller = SpudsController(request.current_role, venue_id)
    # spuds = []
    #
    # # for data_id in request.POST.get('spuds').split('|'):
    # #     spuds.append(controller.get_unapproved_spud_by_id(data_id))
    #
    # controller.approve_spuds(spuds, venue_id)
    
    return HttpResponseRedirect('/venues/get_instagram_stream/%s' % venue_id)


def save_cover(request, venue_id):
    venue = Venue.objects.get(id=venue_id)
    save_cover_image_from_request(venue, request)

    return HttpResponse()


def reset_cover(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    reset_cover_image(venue)

    return HttpResponse('OK')
    
    
def delete_spud_endpoint(request, venue_id):
    try:
        venue = Venue.objects.get(pk = venue_id)
        
        storage = KrowdIOStorage.objects.get(venue = venue)
        delete_spud(storage, request.POST.get('spud_id'))
    except Exception, e:
        logging.error(e.message)
        return HttpResponse(status=500)


def edit_cover(request, venue_id):
    venue = Venue.objects.get(id=venue_id)

    return render(request, 'components/coverimage/edit_cover_image.html', {
        'name': venue.aka_name,
        'return_url': "/venues/view/%s" % venue.id,
        'post_url': '/venues/save_cover/%s' % venue.id,
        'reset_url': '/venues/reset_cover/%s' % venue.id
    })

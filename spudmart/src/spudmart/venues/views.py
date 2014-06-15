from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from spudmart.utils.system_messages import add_system_message
from spudmart.venues.models import Venue, VenueRentStatus
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed
from django.contrib.auth import authenticate, login
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

# DO NOT REMOVE, PLEASE! It's needed for testing purpose
# 
# def login_view(request):
#     errors = []
#     if request.method == 'POST':
#         username = request.POST['email']
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)
#         if not user:
#             errors.append('Wrong username/password')
#         else:
#             login(request, user)
#             return HttpResponseRedirect('/venues/list')
#     
#     return render(request, 'venues/login.html', { 'errors' : errors })

def view(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    splitted_address = venue.medical_address.split(', ')
    medical_address = {
        'address': splitted_address.pop(0) if splitted_address else '',
        'city': splitted_address.pop(0) if splitted_address else '',
        'state': splitted_address.pop(0) if splitted_address else '',
        'zip': splitted_address.pop(0) if splitted_address else ''
    }
    
    is_recipient = VenueRecipient.objects.filter(groundskeeper = request.user)
    rent_venue_url = False
    can_edit = request.user.is_authenticated() and (request.user.pk == venue.user.pk or (venue.renter and request.user.pk == venue.renter.pk))
    
    if venue.price > 0.0 and request.user.is_authenticated() and request.user.pk != venue.user.pk:
        rent_venue_url = get_rent_venue_cbui_url(venue)
    
    sponsor = SponsorPage.objects.filter(sponsor=venue.renter)
    
    return render(request, 'venues/view.html', {
        'venue': venue,
        'sports': ['Football', 'Soccer'],
        'medical_address': medical_address,
        'is_recipient': is_recipient,
        'rent_venue_url': rent_venue_url,
        'can_edit': can_edit,
        'sponsor': sponsor[0] if len(sponsor) else None,
        'is_sponsor': len(sponsor) and sponsor[0].sponsor == request.user
    })

def create(request):
    if request.method == 'POST' and isinstance(request.user, User):
        venue = Venue(user = request.user, sport = request.POST['sport'])
        venue.latitude = float(request.POST['latitude'])
        venue.longitude = float(request.POST['longitude'])
        venue.save()
        return HttpResponseRedirect('/venues/view/%s' % venue.id)
    elif request.method == 'POST':
        return HttpResponseRedirect('/accounts/login?next=/venues/create')
    return render(request, 'venues/create.html', {'sports' : ['Football', 'Soccer'] })

def index(request):
    return render(request, 'venues/index.html')

@login_required
def list_view(request):
    venues = []
    if is_sponsor(request.user):
        venues.extend(Venue.objects.filter(renter = request.user))
        template = 'venues/list_sponsor.html'
    else:
        venues.extend(Venue.objects.filter(user = request.user))
        template = 'venues/list.html'
    return render(request, template, { 'venues' : venues })

# VENUE ENDPOINTS

def save_coordinates(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue.latitude = float(request.POST['latitude'])
    venue.longitude = float(request.POST['longitude'])
    venue.save()
    return HttpResponse('OK')

def save_parking_details(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue.parking_details = request.POST['parking-details']
    venue.parking_tips = request.POST['parking-tips']
    venue.save()
    return HttpResponse('OK')

def save_venue_pics(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue.venue_pics.extend(request.POST.getlist('venue_pics[]'))
    venue.save()
    return HttpResponse('OK')

def save_logo_and_name(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    request_logo = request.POST.getlist('logo[]')
    if len(request_logo):
        logo_id = request_logo[0].split('/')[3]
        logo = UploadedFile.objects.get(pk = logo_id)
        venue.logo = logo
    venue.name = request.POST['name']
    venue.aka_name = request.POST['aka_name']
    venue.save()
    return HttpResponse('OK')

def save_playing_surface_pics(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue.playing_surface_pics.extend(request.POST.getlist('playing_surface_pics[]'))
    venue.playing_surface_details = request.POST['playing_surface_details']
    venue.save()
    return HttpResponse('OK')

def save_video(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue.video = request.POST['video']
    venue.save()
    return HttpResponse('OK')

def save_restroom_details(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue.restroom_details = request.POST['restroom_details']
    venue.restroom_pics.extend(request.POST.getlist('restroom_pics[]'))
    venue.save()
    return HttpResponse('OK')

def save_concession_details(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue.concession_details = request.POST['concession_details']
    venue.save()
    return HttpResponse('OK')

def save_admission_details(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue.admission_details = request.POST['admission_details']
    venue.save()
    return HttpResponse('OK')

def save_shelter_details(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue.shelter_details = request.POST['shelter_details']
    venue.save()
    return HttpResponse('OK')

def save_medical_details(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue.medical_details = request.POST['medical_details']
    venue.medical_address = request.POST['medical_address']
    venue.save()
    return HttpResponse('OK')

def save_handicap_details(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue.handicap_details = request.POST['handicap_details']
    venue.save()
    return HttpResponse('OK')

def send_message(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    message = request.POST.get('message', '')
    to = []
    to.append('support@spudder.zendesk.com')
    to.append(venue.user.email)
    mail.send_mail(subject='Message from Spudmart about Venue: %s' % venue.name, body=message, sender='help@spudder.com', to=to)
    
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
    return render(request, 'venues/recipient/recipient.html', {
                    'cbui_url' : get_venue_recipient_cbui_url(venue)
                  })
    
    
def complete(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    recipient, _ = VenueRecipient.objects.get_or_create(groundskeeper = venue.user)
    recipient.status_code = AmazonActionStatus.get_from_code(request.GET.get('status'))

    if recipient.status_code is AmazonActionStatus.SUCCESS:
        state = RecipientRegistrationState.FINISHED
        recipient.recipient_token_id=request.GET.get('tokenID')
        recipient.refund_token_id=request.GET.get('refundTokenID')
        redirect_to = '/venues/recipient/%s/thanks' % venue_id
    else:
        state = RecipientRegistrationState.TERMINATED
        redirect_to = '/venues/recipient/%s/error' % venue_id

    recipient.state = state
    recipient.save()

    return HttpResponseRedirect(redirect_to)


def thanks(request, venue_id):
    return render(request, 'venues/recipient/thanks.html', {
        'spudder_url': '%s/venues/view/%s' % (settings.SPUDMART_BASE_URL, venue_id)
    })


def error(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    recipient = VenueRecipient.objects.get_or_create(groundskeeper = venue.user)
    status_message = AmazonActionStatus.get_status_message(recipient.status_code)

    return render(request, 'dashboard/recipient/error.html', {
        'spudder_url': '%s/venues/view/%s' % (settings.SPUDMART_BASE_URL, venue_id),
        'status': status_message
    })
    
def rent_complete(request, venue_id):
    venue = get_object_or_404(Venue, pk = venue_id)
    rent_venue, _ = RentVenue.objects.get_or_create(venue=venue, donor=request.user)
    rent_venue.status_code = AmazonActionStatus.get_from_code(request.GET.get('status'))
    
    if rent_venue.status_code is AmazonActionStatus.SUCCESS:
        recipients = VenueRecipient.objects.filter(groundskeeper=venue.user)
        recipientTokenId = recipients[0].recipient_token_id
        
        try:
            connection = get_fps_connection()
            transaction_amount = venue.price
            venue_ipn_url = get_rent_venue_ipn_url(venue, request.user)

            connection.pay(
                RecipientTokenId=recipientTokenId,
                TransactionAmount=transaction_amount,
                SenderTokenId=request.GET.get('tokenID'),
                ChargeFeeTo='Caller',
                MarketplaceVariableFee='5',
                OverrideIPNURL=venue_ipn_url
            )
            
            rent_venue.sender_token_id = request.GET.get('tokenID')
            state = DonationState.PENDING

            venue.renting_status = VenueRentStatus.RESERVED
            venue.save()

            redirect_to = '/venues/rent_venue/%s/thanks' % venue.pk
        except Exception, e:
            state = DonationState.TERMINATED
            rent_venue.status_code = AmazonActionStatus.SE
            rent_venue.error_message = e

            venue.renting_status = VenueRentStatus.FREE
            venue.save()

            redirect_to = '/venues/rent_venue/%s/error' % venue.pk
    else:
        state = DonationState.TERMINATED
        rent_venue.error_message = request.GET.get('errorMessage', '')
        redirect_to = '/venues/rent_venue/%s/error' % venue.pk

    rent_venue.state = state
    rent_venue.save()

    return HttpResponseRedirect(redirect_to)


def rent_thanks(request, venue_id):
    return render(request, 'venues/rent_venue/thanks.html', {
        'spudder_url': '%s/venues/view/%s' % (settings.SPUDMART_BASE_URL, venue_id)
    })
    

def rent_error(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)
    rent_venue = RentVenue.objects.get(venue=venue)
    status_message = AmazonActionStatus.get_status_message(rent_venue.status_code)

    return render(request, 'venues/rent_venue/error.html', {
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

    if IPNTransactionStatus.SUCCESS == parsed_status.transactionStatus:
        rent_venue.state = DonationState.FINISHED
        rent_venue.status_code = AmazonActionStatus.SUCCESS
        rent_venue.save()

        venue.renter = user
        venue.renting_status = VenueRentStatus.RENTED
        venue.save()

        message_body = render_to_string('venues/rent_venue/rent_successful.html', {
            'venue': venue,
            'venue_url': '%s/venues/view/%s' % (settings.SPUDMART_BASE_URL, venue.id),
            'sponsor_page_url': '%s/dashboard/sponsor/page' % settings.SPUDMART_BASE_URL
        })

        add_system_message(body=message_body, user=user)

    elif IPNTransactionStatus.PENDING != parsed_status.transactionStatus:  # ERROR
        rent_venue.state = DonationState.TERMINATED
        rent_venue.status_code = AmazonActionStatus.PE
        rent_venue.error_message = parsed_status.statusMessage
        rent_venue.save()

        venue.renting_status = VenueRentStatus.FREE
        venue.save()

        message_body = render_to_string('venues/rent_venue/rent_error.html', {
            'venue': venue,
            'error_message': rent_venue.error_message,
            'venue_url': '%s/venues/view/%s' % (settings.SPUDMART_BASE_URL, venue.id)
        })

        add_system_message(body=message_body, user=user)

    return HttpResponse('OK')

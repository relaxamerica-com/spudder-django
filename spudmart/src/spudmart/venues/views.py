from django.shortcuts import render, get_object_or_404
from spudmart.venues.models import Venue
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login
from spudmart.upload.models import UploadedFile
import simplejson
from spudmart.recipients.models import VenueRecipient,\
    RecipientRegistrationState, Recipient
from spudmart.amazon.utils import get_venue_recipient_cbui_url,\
    get_rent_venue_cbui_url, get_fps_connection
from spudmart.amazon.models import AmazonActionStatus
import settings
from spudmart.donations.models import RentVenue, DonationState
from google.appengine.api import mail
from django.contrib.auth.decorators import login_required
from spudmart.campusrep.models import School, Student, STATES
from django.core.exceptions import ObjectDoesNotExist

def view(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    splitted_address = venue.medical_address.split(', ')
    medical_address = {
        'address' : splitted_address.pop(0) if splitted_address else '',
        'city' : splitted_address.pop(0) if splitted_address else '',
        'state' : splitted_address.pop(0) if splitted_address else '',
        'zip' : splitted_address.pop(0) if splitted_address else ''
    }
    
    is_recipient = VenueRecipient.objects.filter(groundskeeper = request.user)
    rent_venue_url = False
#     can_edit = request.user.is_authenticated() and (request.user.pk == venue.user.pk or (venue.renter and request.user.pk == venue.renter.pk))
    
    if venue.price > 0.0 and request.user.is_authenticated() and request.user.pk != venue.user.pk:
        rent_venue_url = get_rent_venue_cbui_url(venue)
    
    return render(request, 'venues/view.html', { 
                'venue' : venue,
                'sports' : ['Football', 'Soccer'],
                'medical_address' : medical_address,
                'is_recipient' : is_recipient,
                'rent_venue_url' : rent_venue_url,
                'can_edit' : True
                })

def create(request):
    if request.method == 'POST' and isinstance(request.user, User):
        venue = Venue(user = request.user)
        venue.save()
        return HttpResponseRedirect('/venues/view/%s' % venue.id)
    elif request.method == 'POST':
        return HttpResponseRedirect('/accounts/login?next=/venues/create')
    return render(request, 'venues/create.html', {'sports' : ['Football', 'Soccer'] })

def index(request):
    return render(request, 'venues/index.html')

@login_required
def list_view(request):
    return render(request, 'venues/list.html', { 'venues' : Venue.objects.filter(user = request.user) })

# VENUE ACCOUNTS

def login_view(request):
    errors = []
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if not user:
            errors.append('Wrong username/password')
        else:
            login(request, user)
            return HttpResponseRedirect('/venues/list')
    
    return render(request, 'venues/login.html', { 'errors' : errors })

def register(request, code = None):
    sorted_states = sorted(STATES.items(), key = lambda x:x[1])
    
    if request.method == 'POST':
        return register_with_state(request, state = request.POST['state'], code = code)    

    return render(request, 'venues/register.html', { 
                                                    'states' : sorted_states, 
                                                    'code' : code, 
                                                    })

def register_with_state(request, state, code = None):
    try:
        school = request.POST['school']
    except MultiValueDictKeyError:
        schools = []
        for s in School.objects.filter(state = state):
            schools.append(s)
        schools = sorted(schools, key = lambda sch: sch.name)
        return render(request, 'venues/register_state.html', { 
                                                              'state' : STATES[state], 
                                                              'abbr' : state, 
                                                              'schools' : schools,
                                                              'code' : code,
                                                              })
    else:
        if code:
            return HttpResponseRedirect("/venues/%s/%s/%s"%(state, school, code))
        return HttpResponseRedirect("/venues/%s/%s/"%(state, school))
        

def register_school(request, state, school_name, code = None):
    referrer = None
    if code:
        referrer = Student.objects.get(referral_code = code)
    try:
        school = School.objects.get(state = state.upper(), name = school_name.replace('_', ' '))
    except:
        # Later point to better error page
        return HttpResponse("Error")
    else:
        errors = []
        if request.method == 'POST':
            username = request.POST['email']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if password1 != password2:
                errors.append('Passwords did not match')
            else:
                # We should do checking to see if the user has already registered
                user = User.objects.create_user(username, username, password1)
                user.save()
                
                # Create the student
                student = Student(user = user, school = school)
                
                # Add referral info if it exists
                try:
                    code = request.POST['code']
                except MultiValueDictKeyError:
                    pass
                else:
                    stud = Student.objects.get(referral_code = code)
                    student.referred_by = stud.user
                    
                # See if the school needs a head student, and if so assign this student
                try:
                    school.get_head_student()
                except ObjectDoesNotExist:
                    student.isHead = True
                
                student.save()
                
                return HttpResponseRedirect('/venues/login')
        
        return render(request, 'venues/school_register.html', { 
                                                               'errors' : errors , 
                                                               'school': school, 
                                                               'referrer' : referrer, 
                                                               'code' : code,
                                                               })

# School splash page
def school(request, state, school_name):
    try:
        school = School.objects.get(state = state.upper(), name = school_name.replace('_', ' '))
    except:
        # Later point to better error page
        return HttpResponse("Error")
    else:
        try:
            head = school.get_head_student()
        except ObjectDoesNotExist:
            return render(request, 'venues/school_splash.html', { 'school': school })
        else:
            return render(request, 'venues/school_splash.html', { 
                                                                 'school': school,
                                                                 'head' : head,
                                                                  })
            
# Customize school splash page
def save_school(request, state, school_name):
    """
    Updates school mascot and logo.
    
    Args:
        request: the HttpRequest object, should contain POST data including
            the logo and mascot to be updated
        state: the state in which the school is located, to find school in db 
        school_name: the name of the school, to find school in db
    Returns:
        if POST request: A blank HttpResponse object (code 200)
        if not: a HttpResponseNotAllowed object (code 405)
    """
    
    if request.method == 'POST':
        school = School.objects.get(state=state, name=school_name)
        
        # For logo
        request_logo = request.POST.getlist('logo[]')
        if len(request_logo):
            logo_id = request_logo[0].split('/')[3]
            logo = UploadedFile.objects.get(pk = logo_id)
            school.logo = logo
        
        # For mascot
        mascot = request.POST['mascot']
        if mascot != '':
            school.mascot = mascot
            
        school.save()
        
        return HttpResponse()
    else:
        return HttpResponseNotAllowed(['POST']) 
    

def import_school_data(request):
    if request.method == 'POST':
        import_schools()
    else:
        return HttpResponseNotAllowed(['POST'])

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
    venue.sport = request.POST['sport']
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
    venue.price = int(request.POST['price'])
    venue.save()
    return HttpResponse('OK')

def get_venues_within_bounds(request):
    latitude_range = [float(value) for value in request.GET.getlist('latitude_range[]')]
    longitude_range = [float(value) for value in request.GET.getlist('longitude_range[]')]
    
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
    
    if list_type == 'venue_pics':
        the_list = venue.venue_pics
    else:
        the_list = venue.playing_surface_pics
        
    if file_url in the_list:
        the_list.remove(file_url)
        
    if list_type == 'venue_pics':
        venue.venue_pics = the_list
    else:
        venue.playing_surface_pics = the_list
    
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
            transactionAmount = venue.price
            connection.pay(RecipientTokenId=recipientTokenId, TransactionAmount=transactionAmount,
                           SenderTokenId=request.GET.get('tokenID'), ChargeFeeTo='Caller',
                           MarketplaceVariableFee='5')
            
            rent_venue.sender_token_id = request.GET.get('tokenID')
            state = DonationState.FINISHED
            venue.renter = request.user
            venue.save()
            redirect_to = '/venues/rent_venue/%s/thanks' % venue.pk
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


def rent_thanks(request, venue_id):

    url = '%s/venues/view/%s' % (
        settings.SPUDMART_BASE_URL,
        venue_id)

    return render(request, 'venues/rent_venue/thanks.html', {
        'spudder_url': url
    })
    

def rent_error(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)
    status_message = AmazonActionStatus.get_status_message(venue.status_code)
    rent_venue, _ = RentVenue.objects.get_or_create(venue=venue, donor=request.user)

    url = '%s/venues/view/%s' % (
        settings.SPUDMART_BASE_URL,
        venue.id)

    return render(request, 'venues/rent_venue/error.html', {
        'spudder_url': url,
        'status': status_message,
        'error_message': rent_venue.error_message
    })
from django.shortcuts import render
from spudmart.venues.models import Venue
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login
from spudmart.upload.models import UploadedFile
import logging
import simplejson

def view(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    return render(request, 'venues/view.html', { 
                'venue' : venue,
                'sports' : ['Football', 'Soccer'] 
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

def register(request):
    errors = []
    if request.method == 'POST':
        username = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 != password2:
            errors.append('Passwords did not match')
        else:
            user = User.objects.create_user(username, username, password1)
            user.save()
            return HttpResponseRedirect('/venues/login')
    
    return render(request, 'venues/register.html', { 'errors' : errors })

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
    venue.venue_pics = request.POST.getlist('venue_pics[]')
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
    venue.playing_surface_pics = request.POST.getlist('playing_surface_pics[]')
    venue.playing_surface_details = request.POST['playing_surface_details']
    venue.save()
    return HttpResponse('OK')

def save_video_url(request, venue_id):
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

def save_price(request, venue_id):
    venue = Venue.objects.get(pk = venue_id)
    venue.price = int(request.POST['price'])
    venue.save()
    return HttpResponse('OK')

def get_venues_within_bounds(request):
    latitude_range = [float(value) for value in request.GET['latitude_range'].split('|')]
    longitude_range = [float(value) for value in request.GET['longitude_range'].split('|')]
    
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
                'longitude' : venue.longitude
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
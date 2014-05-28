import json

from django.http import HttpResponse
from spudmart.api import api_settings

from spudmart.venues.models import Venue

"""

API Key verification

"""

def verify_api_key(key):
    if key == api_settings.spudmart_api_key:
        return True

    return False

"""

Key Authentication Error JSON String

"""


def key_authentication_error():
    return {"meta": {"error_type": "invalid_key_error", "code": 002, "error_message": "Invalid API Key Specified"}}


"""

Missing Parameters Error JSON String

"""


def missing_parameters_error():
    return {"meta": {"error_type": "missing_parameters", "code": 003, "error_message": "API Parameters Missing"}}


"""

The API Landing

"""


def index(request):
    pass


"""

Returns all the venues from SpudMart in JSON Format

"""


def get_venues(request):
    if request.method == 'GET':
        if 'key' in request.GET and request.GET['key'] != '':
            if verify_api_key(request.GET['key']):
                venues = Venue.objects.all()

                venues_json = []

                for venue in venues:
                    venues_json.append({'id': venue.id, 'lat': venue.latitude, 'lon': venue.longitude})

                return_json = {'venues': venues_json}

                return HttpResponse(json.dumps(return_json), content_type='application/json')
            else:
                return HttpResponse(json.dumps(key_authentication_error()), content_type='application/json')

    return HttpResponse(json.dumps(missing_parameters_error()), content_type='application/json')



"""

Saves posts sent in via JSON using HTTP POST

"""


def save_posts_for_venue(request):
    pass
from threading import Thread
from django.http import HttpResponse
from models import APIKeys

import socialnetworks
import spice_settings
import json
import spudmart.api

"""

The async function wrapper

"""

def async(gen):
    def func(*args, **kwargs):
        it = gen(*args, **kwargs)
        result = it.next()
        Thread(target=lambda: list(it)).start()
        return result
    return func

"""

API Landing function

"""

def api_landing(request) :
    return HttpResponse('{"meta":{"error_type":"invalid_entry_point","code":001,"error_message":"Invalid API Entry Point"}}', content_type="application/json")

"""

Validate if API Key is valid

"""

def validate_api_key(api_key) :
    auth_method = spice_settings.api_auth_method

    # Use static API key in the settings
    if auth_method == "static" :
        if api_key == spice_settings.static_api_key :
            return True

    # Use database API key
    elif auth_method == "dynamic" :
        api_key = APIKeys.objects.filter(api_key = api_key, is_active = True)

        if(len(api_key) > 0) :
            return True

    return False

"""

Key Authentication Error JSON String

"""

def key_authentication_error() :
    return { "meta": { "error_type":"invalid_key_error", "code":002,"error_message":"Invalid API Key Specified" }}

"""

Missing Parameters Error JSON String

"""

def missing_parameters_error() :
    return { "meta": { "error_type":"missing_parameters", "code":003,"error_message":"API Parameters Missing" }}

"""

Perform a social media query

"""

@async
def location(request) :
    # Begin processing
    # Response object
    json_response = []

    # Verify if HTTP GET
    if request.method == 'GET':

        if ('lat' in request.GET and request.GET['lat'] != '') and  \
            ('lon' in request.GET and request.GET['lon'] != '') and \
            ('venueid' in request.GET and request.GET['venueid'] != '') and \
            ('key' in request.GET and request.GET['key'] != '') :

            latitude = request.GET["lat"]
            longitude = request.GET["lon"]
            api_key = request.GET["key"]
            venue_id = request.GET["venueid"]

            if(validate_api_key(api_key)) :
                # Return a quick response with OK status
                yield HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')

                for social_network in spice_settings.social_networks :
                    json_response.append( { social_network : getattr('socialnetworks.' + social_network, "location_data")(latitude, longitude)} )

                json_response = { 'venue_id' : venue_id, 'data' : json_response }

                # Return JSON document to SpudMart
                spudmart.api.send_posts_for_venue(json_response)

            else :
                # Return a quick response with Error status
                yield HttpResponse(json.dumps({'status': 'error', 'error' : key_authentication_error() }), content_type='application/json')

        else :
            # Return a quick response with Error status
            yield HttpResponse(json.dumps({'status': 'error', 'error' : missing_parameters_error() }), content_type='application/json')



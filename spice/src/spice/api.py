from threading import Thread
import json

from django.http import HttpResponse
import spice_settings

import spice.spudmart.api
import spice.socialnetworks

import logging

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


def api_landing(request):
    return HttpResponse(
        '{"meta":{"error_type":"invalid_entry_point","code":001,"error_message":"Invalid API Entry Point"}}',
        content_type="application/json")


"""

Validate if API Key is valid

"""


def validate_api_key(api_key):
    auth_method = spice_settings.api_auth_method

    # Use static API key in the settings
    if auth_method == "static":
        if api_key == spice_settings.static_api_key:
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

Perform a social media query

"""


@async
def location(request):
    logging.debug("SPICE: api/locations stated")

    # Begin processing
    # Response object
    json_response = []

    # Verify if HTTP GET
    if request.method == 'GET':
        if 'key' in request.GET and request.GET['key'] != '':

            api_key = request.GET["key"]

            if validate_api_key(api_key):
                # Return a quick response with OK status
                yield HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')

                venues_json = json.load(spice.spudmart.api.call_venues_api())

                for venue in venues_json.venues:

                    latitude = venue.lat
                    longitude = venue.lon

                    venue_social_network_json = []

                    for social_network in spice_settings.social_networks:
                        venue_social_network_json.append({social_network: getattr('socialnetworks.' + social_network,
                                                                                  "location_data")(latitude,
                                                                                                   longitude)})

                    json_response.append({'venue_id': venue.venue_id, 'data': venue_social_network_json})

                spice.spudmart.api.send_posts_for_venue(json_response)

                logging.debug("SPICE: api/locations finished")

            else:
                # Return a quick response with Error status
                yield HttpResponse(json.dumps({'status': 'error', 'error': key_authentication_error()}),
                                   content_type='application/json')

        else:
            # Return a quick response with Error status
            yield HttpResponse(json.dumps({'status': 'error', 'error': missing_parameters_error()}),
                               content_type='application/json')
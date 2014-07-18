import json

from django.http import HttpResponse
import spice_settings

import spuddersocialengine.spudmart.api
import spuddersocialengine.socialnetworks

from spuddersocialengine.models import *

import logging
import importlib

from google.appengine.api import taskqueue


"""

API Landing function

"""


def api_landing(request):
    return HttpResponse(json.dumps(invalid_api_entry_error()), content_type="application/json")


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

Invalid API Entry

"""


def invalid_api_entry_error():
    return {"meta": {"error_type": "invalid_key_error", "code": 001, "error_message": "Invalid API Entry Point"}}


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


def location(request):
    logging.debug("SPICE: api/locations started")

    # Verify if HTTP GET
    if request.method == 'GET':
        if 'key' in request.GET and request.GET['key'] != '':

            api_key = request.GET["key"]

            if validate_api_key(api_key):
                # Add task to queue
                location_queue = taskqueue.Queue('locationtask')
                task = taskqueue.Task(url='/socialengine/api/location_task?key=' + api_key, method='GET')
                location_queue.add(task)

                logging.debug("SPICE: api/locations finished")

                # Return a quick response with OK status
                return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')
            else:
                # Debug logging
                logging.debug("SPICE: api/locations finished: key_authentication_error")

                # Return a quick response with Error status
                return HttpResponse(json.dumps({'status': 'error', 'error': key_authentication_error()}),
                                    content_type='application/json')

        else:
            # Debug logging
            logging.debug("SPICE: api/locations finished: missing_parameters_error")

            # Return a quick response with Error status
            return HttpResponse(json.dumps({'status': 'error', 'error': missing_parameters_error()}),
                                content_type='application/json')
    else:
        # Debug logging
        logging.debug("SPICE: api/locations finished: method not GET")


"""

To be used as a task. Invoked by the location call

"""


def location_task(request):
    logging.debug("SPICE: api/location_task started")

    # Begin processing
    # Response object

    json_response = []

    if request.method == 'GET':
        if 'key' in request.GET and request.GET['key'] != '':
            api_key = request.GET["key"]

            if validate_api_key(api_key):

                # Get the venues from spudmart
                venues_json = spuddersocialengine.spudmart.api.call_venues_api(request)
                venues_data = json.loads(venues_json)

                # Save venues into the database
                save_venues(venues_data)

                # For debugging purposes
                venue_count = 0

                for venue in venues_data['venues']:

                    venue_count += 1

                    # Log the current venue count
                    logging.debug("Venue #%i", venue_count)

                    latitude = venue['lat']
                    longitude = venue['lon']
                    venue_id = venue['id']

                    venue_social_network_json = []

                    for social_network in spice_settings.social_networks:

                        social_network_name = social_network['name']
                        social_network_type = social_network['meta']['type']
                        social_network_enabled = social_network['enabled']

                        if social_network_type == "polling" and social_network_enabled:
                            # Has a dedicated class to poll for data
                            venue_social_network_json.append(
                                {social_network: getattr(
                                    importlib.import_module('spuddersocialengine.socialnetworks.' + social_network_name),
                                    "location_data")(request, latitude, longitude, venue_id)})
                        elif social_network_type == "subscription" and social_network_enabled:
                            # Deal with the subscription
                            getattr(importlib.import_module('spuddersocialengine.socialnetworks.' + social_network_name),
                                    "process_data")(request, latitude, longitude, venue_id)

                        # Debug logging of images returned back
                        logging.debug("SPICE: api/location_task venue id %s completed", (venue['id']))

                    # Main JSON append
                    json_response.append({'venue_id': venue['id'], 'data': venue_social_network_json})

                spuddersocialengine.spudmart.api.send_posts_for_venue(json_response)
            else:
                logging.debug("SPICE: api/location_task : invalid API Key")

    # Debug logging: end of method call
    logging.debug("SPICE: api/location_task finished")

    # Remove from the queue

    queue_item = taskqueue.Queue('locationtask')
    queue_item.purge()

    return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')


"""

Manual Processing call

"""


def manual_process(request):
    logging.debug("SPICE: api/manual_process started")

    venues_return = []

    if request.method == 'GET':
        if ('key' in request.GET and request.GET['key'] != '') and \
                ('venue_id' in request.GET and request.GET['venue_id'] != ''):
            api_key = request.GET["key"]
            venue_id = request.GET["venue_id"]

            if validate_api_key(api_key):
                social_networks = spice_settings.social_networks

                for social_network in social_networks:

                    venue_return = getattr(importlib.import_module('spuddersocialengine.socialnetworks.' + social_network['name']),
                                           "manual_process_for_venue")(venue_id)

                    if venue_return is not None:
                        venues_return.append(venues_return)

                spuddersocialengine.spudmart.api.send_posts_for_venue(venues_return)

            else:
                logging.debug("SPICE: api/manual_process : invalid API Key")

                return HttpResponse(json.dumps(key_authentication_error()), content_type='application/json')

    logging.debug("SPICE: api/manual_process ended")

    return HttpResponse(json.dumps(venues_return), content_type='application/json')


"""

Save (Add / Remove) venues from the database

"""


def save_venues(venues_data):
    logging.debug("SPICE: api/save_venues started")
    # Save venues not in the database
    venues_ids_array = []

    social_networks = spice_settings.social_networks

    # Create new venues
    for venue in venues_data['venues']:
        latitude = venue['lat']
        longitude = venue['lon']
        venue_id = str(venue['id'])

        venues_ids_array.append(venue_id)

        venue_by_id = VenuesModel.objects.filter(venue_id=venue_id)

        if len(venue_by_id) < 1:
            logging.debug("SPICE: api/save_venues creating new venue for venue_id: %s" % venue_id)
            new_venue = VenuesModel(venue_id=venue_id, lat=latitude, lon=longitude)
            new_venue.save()

            # Get each social network to register: Where applicable
            for social_network in social_networks:
                logging.debug("SPICE: api/save_venues register venue for social network %s" % social_network['name'])
                getattr(importlib.import_module('spuddersocialengine.socialnetworks.' + social_network['name']),
                        "register_venue")(venue_id)


    # Cleanup unwanted venues from the call
    all_venues = VenuesModel.objects.all()

    logging.debug("SPICE: api/save_venues venues in the array: %s" % json.dumps(venues_ids_array))

    for venue in all_venues:
        venue_found = False

        for venue_item in venues_ids_array:
            if venue_item == venue.venue_id:
                venue_found = True

        if venue_found == False:
            try:
                logging.debug("SPICE: api/save_venues attempting to remove venue_id %s" % venue.venue_id)
                venue_to_find = VenuesModel.objects.get(venue_id=venue.venue_id)
                venue_to_find.delete()

                # Get each social network to de-register: Where applicable
                for social_network in social_networks:
                    logging.debug("SPICE: api/save_venues deregister on network %s" % social_network['name'])
                    getattr(importlib.import_module('spuddersocialengine.socialnetworks.' + social_network['name']),
                            "deregister_venue")(venue_to_find.venue_id)
            except VenuesModel.DoesNotExist:
                # Nothing to do if it does not exist
                pass
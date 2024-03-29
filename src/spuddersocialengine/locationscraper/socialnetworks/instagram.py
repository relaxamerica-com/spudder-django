import urllib
import hmac
import hashlib
import httplib
import logging
from django.conf import settings
from google.appengine.api import taskqueue
from spuddersocialengine.locationscraper.socialnetworks import instagram_settings
from spuddersocialengine.locationscraper.api import *
from spuddersocialengine.locationscraper.spudmart.api import *
from spuddersocialengine.locationscraper.spudmart import api as spudmart_api
from spuddersocialengine.locationscraper.models import InstagramPerSportApplicationConfiguration
from spuddersocialengine.models import SpudFromSocialMedia


"""

Creates a new Instagram Subscription and returns the JSON back

"""


def create_new_subscription(request, latitude, longitude, sport):
    # Perform subscription

    # Variables
    url_string = "api.instagram.com"
    path_to_callback = "%s/%s" % (
        request.build_absolute_uri(location='instagram/callback'),
        ''.join([s.lower() for s in sport if s.isalnum()]))
    logging.debug("SPICE: socialnetworks/instagram/process_data callback URL: %s" % path_to_callback)

    config = InstagramPerSportApplicationConfiguration.GetForSport(sport)
    if not config.client_id or not config.client_secret:
        logging.error(
            "locationscraper.instagram.create_new_subscription: Can not create subscription for sport: %s, "
            "No InstagramPerSportApplicationConfiguration object configured." % sport)
        return

    # Perform the request
    data = urllib.urlencode(
        {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'object': 'geography',
            'aspect': 'media',
            'lat': latitude,
            'lng': longitude,
            'radius': str(int(config.default_distance/3)),
            'callback_url': path_to_callback,
        }
    )

    # Make a POST request to the subscription service
    connection = httplib.HTTPSConnection(url_string)
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    connection.request(method='POST', url='/v1/subscriptions/', body=data, headers=headers)
    content_to_return = connection.getresponse()

    content_to_return = json.loads(content_to_return.read())

    return content_to_return

"""

Get location data

"""


def process_data(request, latitude, longitude, venue_id, sport):
    # Debug logging of instagram
    logging.debug("SPICE: socialnetworks/instagram/process_data started")

    content_to_return = None

    all_active_subscriptions = InstagramSubscriptions.objects.filter(venue_id=venue_id)

    # Check to see if the subscription exists in the database otherwise create it
    if len(all_active_subscriptions) < 1:
        # Add to the database and order a subscription
        logging.debug("SPICE: socialnetworks/instagram/process_data register new venue ID %s", venue_id)

        content_to_return = create_new_subscription(request, latitude, longitude, sport)
        if content_to_return and 'data' in content_to_return:
            # Save the subscription tagged with the ID to the database
            subscriptions_for_the_venue = content_to_return['data']

            logging.debug("SPICE: socialnetworks/instagram/process_data data from call: %s" %
                          json.dumps(subscriptions_for_the_venue))

            if 'id' in subscriptions_for_the_venue:
                # Looks to be a single item, not array
                new_subscription = InstagramSubscriptions(
                    venue_id=venue_id,
                    subscription_id=subscriptions_for_the_venue['id'],
                    sport=sport)
                new_subscription.save()
            else:
                # Looks to be an array
                for subscription in subscriptions_for_the_venue:
                    new_subscription = InstagramSubscriptions(
                        venue_id=venue_id,
                        subscription_id=subscription['id'],
                        sport=sport)
                    new_subscription.save()
        else:
            # If a subscription could not be made then delete the venue model
            if content_to_return:
                logging.error(
                    "locationscraper/instagram/process_data: Content was returned from the subscription service but "
                    "did not contain a valid response. Response was: %s" % content_to_return)
            try:
                VenuesModel.objects.get(venue_id=venue_id).delete()
                logging.debug(
                    "locationscraper/instagram/process_data: deleting VenueModel with id %s as no "
                    "instagram subscription could be create" % venue_id)
            except VenuesModel.DoesNotExist as ex:
                logging.error("%s" % ex)

    # Debug logging of instagram
    logging.debug("SPICE: socialnetworks/instagram/process_data ended")

    return content_to_return


"""

Get access Key from Token

"""


def get_access_key(client_id):
    # Currently not yet supported
    return None


"""

Gets the end result of a callback (returns objects)

"""


def get_instagram_callback_json_end_result(geography_id, config):
    url_to_call = "https://api.instagram.com/v1/geographies/%s/media/recent?client_id=%s" % \
                  (geography_id, config.client_id)

    response = urllib2.urlopen(url=url_to_call)

    return response.read()


"""

The instagram callback URL

"""


def callback(request, sport=None):
    logging.debug("SPICE: socialnetworks/instagram/callback started")

    sport = [s for s in settings.SPORTS if ''.join([c.lower() for c in s if c.isalnum()]) == sport][0]

    if request.method == 'GET':
        if 'hub.mode' in request.GET and request.GET['hub.mode'] != '':
            hub_mode = request.GET['hub.mode']
            hub_challenge = request.GET['hub.challenge']
            hub_verify_token = ""

            if 'hub.verify_token' in request.GET and request.GET['hub.verify_token'] != '':
                hub_verify_token = request.GET['hub.verify_token']

            logging.debug("SPICE: socialnetworks/instagram/callback challange returned: %s", hub_challenge)
            logging.debug("SPICE: socialnetworks/instagram/callback ended")

            return HttpResponse(hub_challenge)
        else:
            logging.debug("SPICE: socialnetworks/instagram/callback ended")

            return HttpResponse("NOK")

    elif request.method == 'POST':
        x_hub_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
        raw_response = request.read()

        config = InstagramPerSportApplicationConfiguration.GetForSport(sport)
        if instagram_verify_signature(config.client_secret, raw_response, x_hub_signature):
            logging.debug("SPICE: socialnetworks/instagram/callback HTTP body: %s", raw_response)

            json_response = json.loads(raw_response)

            for json_response_item in json_response:
                subscription_id = json_response_item.get('subscription_id', None)
                try:
                    # Try get the subscription
                    subscription = InstagramSubscriptions.objects.get(subscription_id=subscription_id)
                    venue_id = subscription.venue_id

                    data = json.loads(get_instagram_callback_json_end_result(json_response_item['object_id'], config))

                    for data_item in data.get('data', []):
                        spud = social_spud_from_instagram_update(data_item, venue_id)

                    # Is the content auto-processor enabled?
                    if instagram_settings.instagram_auto_process_callback:
                        instagram_queue = taskqueue.Queue('instagramcallback')
                        queue_stats = instagram_queue.fetch_statistics()

                        # Only add if there is no task in the queue
                        if queue_stats.tasks < 1:
                            task = taskqueue.Task(
                                url='/socialengine/api/instagram/callback_task?key=' + spice_settings.static_api_key,
                                method='GET')
                            instagram_queue.add(task)

                except InstagramSubscriptions.DoesNotExist:
                    # If the subscription does not exist then deregister it
                    if subscription_id and not InstagramSubscriptions.objects.filter(subscription_id=subscription_id):
                        deregister_subscription(subscription_id, sport)
                        logging.debug("SPICE: socialnetworks/instagram/callback deregistered unknown subscription")
                    pass

        else:
            logging.debug("SPICE: socialnetworks/instagram/callback invalid instagram signature")

        logging.debug("SPICE: socialnetworks/instagram/callback ended")

        return HttpResponse("OK")

"""

Instagram Callback Task

"""


def callback_task(request):
    raise DeprecationWarning('this code is now depricated as it relies on the depricated InstagramDataProcessor')
    logging.debug("SPICE: socialnetworks/instagram/callback_task started")

    spudmart_json = []

    if request.method == 'GET':
        if 'key' in request.GET and request.GET['key'] != '':
            if validate_api_key(request.GET['key']):
                # Process the queue
                items_to_process = None

                # Does venue_id feature in the filter?
                if 'venue_id' in request.GET:
                    items_to_process = InstagramDataProcessor.objects.filter(
                        processed=False, venue_id=request.GET['venue_id'])
                else:
                    items_to_process = InstagramDataProcessor.objects.filter(processed=False)

                for item in items_to_process:
                    data_item = item.data

                    logging.debug("SPICE: socialnetworks/instagram/callback_task processing: %s", data_item)

                    # Try to process
                    if spice_instagram_item_processing(data_item):
                        logging.debug("SPICE: socialnetworks/instagram/callback_task processed")

                        processed_json = process_spudmart_json_item(data_item)

                        if processed_json is not None:
                            spudmart_json.append(processed_json)

                        item.processed = True
                        item.save()
                    else:
                        logging.debug("SPICE: socialnetworks/instagram/callback_task unable_to_process")

                logging.debug("SPICE: socialnetworks/instagram/callback_task ended")

                # Send back to SpudMart
                spudmart_api.send_posts_for_venue(spudmart_json)

                # Finally: Remove all from the queue
                queue_item = taskqueue.Queue('instagramcallback')
                queue_item.purge()

                return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')

    # Finally: Remove all from the queue
    queue_item = taskqueue.Queue('instagramcallback')
    queue_item.purge()

    logging.debug("SPICE: socialnetworks/instagram/callback_task ended. Invalid API Key")
    return HttpResponse(json.dumps(invalid_api_entry_error()), content_type='application/json')

"""

Process and return data for an item to pass to SpudMart

"""


def process_spudmart_json_item(item):
    logging.debug("SPICE: socialnetworks/instagram/process_spudmart_json_item started")

    # Compose a return item back to SpudMart for the venue

    logging.debug("SPICE: socialnetworks/instagram/process_spudmart_json_item ended")

    # Return a SpudMart item
    return None

"""

Manual Process Instagram Entries for each venue

"""


def manual_process_for_venue(venue_id):
    raise DeprecationWarning('this code is now depricated as it relies on the depricated InstagramDataProcessor')
    logging.debug("SPICE: socialnetworks/instagram/process_for_venue started")

    if instagram_settings.instagram_auto_process_callback == False:
        instagram_queue = taskqueue.Queue('instagramcallback')
        queue_stats = instagram_queue.fetch_statistics()

        # Only add if there is no task in the queue
        if queue_stats.tasks < 1:
            task = taskqueue.Task(url='/socialengine/api/instagram/callback_task?key=%s&venue_id=%s' %
                                      (spice_settings.static_api_key, venue_id),
                                  method='GET')
            instagram_queue.add(task)

            logging.debug("SPICE: socialnetworks/instagram/process_for_venue added task for venue_id %s" % venue_id)

    logging.debug("SPICE: socialnetworks/instagram/process_for_venue ended")

    return None

"""

SPICE and Specifically: Instagram Processing

"""


def spice_instagram_item_processing(data_item):
    logging.debug("SPICE: socialnetworks/instagram/spice_instagram_item_processing started")

    data_objects = json.loads('{"data": %s}' % data_item)

    instagram_media = []

    for data_object_item in data_objects['data']:
        # Call instagram and get data about that specific object
        object_id = data_object_item['object_id']
        change_type = data_object_item['changed_aspect']

        if change_type == "media":

            # Make a call to instagram and get media info
            instagram_url = "https://api.instagram.com/v1/geographies/%s/media/recent?client_id=%s" % (object_id, instagram_settings.instagram_client_id)
            instagram_call = urllib2.urlopen(instagram_url)
            instagram_call = instagram_call.read()

            logging.debug("SPICE: socialnetworks/instagram/spice_instagram_item_processing to send: %s" % instagram_call)

            instagram_data = json.loads(instagram_call)
            instagram_data_items = instagram_data['data']

            for instagram_data in instagram_data_items:
                instagram_media.append({
                    'source': 'instagram',
                    'images': str(instagram_data['images']),
                    'user': str(instagram_data['user']),
                    'created_time': str(instagram_data['created_time']),
                    'link': str(instagram_data['link']),
                    'caption': str(instagram_data['caption']),
                    'tags': str(instagram_data['tags']),
                    'type': str(instagram_data['type']),
                    'location': str(instagram_data['location']),
                })

        # Call spudmart and send back values
        send_posts_for_venue(instagram_media)

        logging.debug("SPICE: socialnetworks/instagram/spice_instagram_item_processing ended successfully")

        return True

    logging.debug("SPICE: socialnetworks/instagram/spice_instagram_item_processing not successful")

    return False


"""

Verifies that it is Instagram

"""

def instagram_verify_signature(client_secret, raw_response, x_hub_signature):
    digest = hmac.new(client_secret.encode('utf-8'),
                      msg=raw_response.encode('utf-8'),
                      digestmod=hashlib.sha1
                      ).hexdigest()
    return digest == x_hub_signature

"""

Registers a venue

"""


def register_venue(venue_id):
    # For this specific processor do nothing
    pass


"""

De-register a subscription

"""


def deregister_subscription(subscription_id, sport=None):
    if not sport:
        # This can no longer be done if we don't knowthe sport of the venue
        return
    config = InstagramPerSportApplicationConfiguration.GetForSport(sport)
    instagram_delete_url = "https://api.instagram.com/v1/subscriptions?client_secret=%s&id=%s&client_id=%s" % (
        config.client_secret,
        subscription_id,
        config.client_id)
    request = urllib2.Request(instagram_delete_url)
    request.get_method = lambda: 'DELETE'
    urllib2.urlopen(request)

"""

De-register a venue

"""


def deregister_venue(venue_id):
    subscriptions = InstagramSubscriptions.objects.filter(venue_id=venue_id)

    for subscription in subscriptions:
        # Un-subscribe
        deregister_subscription(subscription.subscription_id, subscription.sport)

        # Delete
        subscription.delete()


def social_spud_from_instagram_update(data, venue_id):
    id = data.get('id', None)
    if not id:
        return None
    type = data.get('type', None)
    if type != "image":
        return None
    if SpudFromSocialMedia.objects.filter(unique_id_from_source=id, originating_service='INSTAGRAM').count():
        return None
    spud = SpudFromSocialMedia(
        entity_type="VENUE",
        entity_id=venue_id,
        originating_service='INSTAGRAM',
        unique_id_from_source=id,
        state=SpudFromSocialMedia.STATE_NEW,
        type=SpudFromSocialMedia.TYPE_IMAGE,
        data=json.dumps({
            'service': 'INSTAGRAM',
            'user': {
                'username': data.get('user', {}).get('username', None),
                'id': data.get('user', {}).get('id', None),
                'profile_picture': data.get('user', {}).get('profile_picture', None)
            },
            'text': [data['caption']['text']] if data.get('caption', None) and 'text' in data['caption'] else [],
            'image': {
                'standard_resolution': {
                    'url': data.get('images', {}).get('low_resolution', {}).get('url', None),
                    'width': data.get('images', {}).get('low_resolution', {}).get('width', None),
                    'height': data.get('images', {}).get('low_resolution', {}).get('height', None),
                }
            }
        }))
    spud.save()
    return spud


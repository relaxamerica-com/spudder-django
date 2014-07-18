import logging
import json
import requests
from requests_oauthlib import OAuth1
from spuddersocialengine import spice_settings

import twitter_settings

from spuddersocialengine.models import TwitterPolling, TwitterDataProcessor
import spuddersocialengine.spice_settings
from spuddersocialengine.spudmart import api as spudmart_api

from django.shortcuts import HttpResponse

"""

Get location data

"""


def location_data(request, latitude, longitude, venue_id):
    # Debug logging of twitter
    logging.debug("SPICE: socialnetworks/twitter/location_data started")

    # Authenticate
    auth = OAuth1(twitter_settings.twitter_client_id, twitter_settings.twitter_client_secret,
                  twitter_settings.twitter_access_token, twitter_settings.twitter_access_token_secret)

    # Get latest ID
    latest_id_exists = True
    since_id = None

    try:
        since_id = TwitterPolling.objects.latest('last_poll_id')
    except TwitterPolling.DoesNotExist:
        latest_id_exists = False

    if not latest_id_exists:
        url = 'https://api.twitter.com/1.1/search/tweets.json?geocode=%s,%s,1km' % (latitude, longitude)
    else:
        url = 'https://api.twitter.com/1.1/search/tweets.json?since_id=%s&geocode=%s,%s,1km' % (since_id,
                                                                                                latitude,
                                                                                                longitude)
    # Send search request
    get_request = requests.get(url, auth=auth)

    # Response JSON
    response_json = json.loads(get_request.text)

    # last_tweet_id of the polling
    last_tweet_id = 0

    for status in response_json['statuses']:
        if status['id'] > last_tweet_id:
            last_tweet_id = status['id']

    # Save last_tweet_id
    polling_result = TwitterPolling(last_poll_id=last_tweet_id)
    polling_result.save()

    # Save the response data
    response_data = TwitterDataProcessor(venue_id=venue_id, data=get_request.text, processed=False)
    logging.debug("SPICE: socialnetworks/twitter/location_data save response json")
    response_data.save()

    # Automatically process content items for this venue ?
    if twitter_settings.twitter_auto_process_content == True:
        manual_process_for_venue(venue_id)

    logging.debug("SPICE: socialnetworks/twitter/location_data ended")


"""

Manual Process Twitter Entries for each venue

"""


def manual_process_for_venue(venue_id):
    logging.debug("SPICE: socialnetworks/twitter/manual_process_for_venue started")

    # Fetch items to process
    items_to_process = TwitterDataProcessor.objects.filter(processed=False,
                                                           venue_id=venue_id)

    # Process each unprocessed item in that venue
    for item_to_process in items_to_process:
        logging.debug("SPICE: socialnetworks/twitter/manual_process_for_venue added task for venue_id %s" % venue_id)
        if process_content_for_spudmart(items_to_process.data):
            item_to_process.processed = True
            item_to_process.save()

    logging.debug("SPICE: socialnetworks/twitter/manual_process_for_venue ended")


"""

This specific function call process content and passes it over to spudmart.

"""


def process_content_for_spudmart(content_json):
    # TODO: Return status of processing when developing SpudMart bridge
    return True


"""

De-register a venue

"""


def deregister_venue(venue_id):
    pass


"""

Registers a venue

"""


def register_venue(venue_id):
    pass
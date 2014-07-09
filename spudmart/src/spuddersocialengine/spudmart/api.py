import spudmart_settings
import urllib2
import json
import logging

"""

Send posts to SpudMart in JSON format

"""


def send_posts_for_venue(json_response):
    # Does nothing at the moment
    pass


"""

Call SpudMart API and get venues

"""


def call_venues_api():
    logging.debug("SPICE: spudmart/api started")

    url_to_call = spudmart_settings.spudmart_api_url + "get_venues?key=" + spudmart_settings.spudmart_api_key

    logging.debug("SPICE: spudmart/api Calling: %s", url_to_call)

    api_request = urllib2.urlopen(url_to_call)
    json_response = json.load(api_request)

    logging.debug("SPICE: spudmart/api finished")
    return json_response

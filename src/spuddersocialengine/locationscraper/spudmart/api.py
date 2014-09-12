import urllib2
import logging

from spuddersocialengine.locationscraper.spudmart import spudmart_settings


"""

Send posts to SpudMart in JSON format

"""


def send_posts_for_venue(json_response):
    # Does nothing at the moment
    pass


"""

Call SpudMart API and get venues

"""


def call_venues_api(request):
    logging.debug("SPICE: spudmart/api started")

    url_to_call = spudmart_settings.spudmart_api_url + "get_venues?key=" + spudmart_settings.spudmart_api_key

    logging.debug("SPICE: spudmart/api Calling: %s", url_to_call)

    json_response = urllib2.urlopen(url_to_call)
    json_response = json_response.read()

    logging.debug("SPICE: spudmart/api returned: %s", json_response)
    logging.debug("SPICE: spudmart/api finished")

    return json_response

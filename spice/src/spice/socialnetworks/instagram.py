import urllib2
import json

from spice.socialnetworks import instagram_settings


"""

Get location data

"""


def location_data(latitude, longitude):
    url_string = ""

    if instagram_settings.instagram_auth_mode == "client_id":
        url_string = 'https://api.instagram.com/v1/media/search?lat=%s&lng=%s&client_id=%s' % (
        latitude, longitude, instagram_settings.instagram_client_id)
    elif instagram_settings.instagram_auth_mode == "client_id":
        instagram_settings.instagram_access_token = get_access_key(instagram_settings.instagram_client_id)
        url_string = 'https://api.instagram.com/v1/media/search?lat=%s&lng=%s&access_token=%s' % (latitude, longitude, instagram_settings.instagram_access_token)

    instagram_request = urllib2.urlopen(url_string)

    # Process the JSON returned document
    instagram_response = json.load(instagram_request)
    response_images_data = instagram_response['data']
    image_response = []

    for image in response_images_data:
        image_response.append({
            'source': 'instagram',
            'images': str(image['images']),
            'user': str(image['user']),
            'created_time': str(image['created_time']),
            'link': str(image['link']),
            'caption': str(image['caption']),
            'tags': str(image['tags']),
            'type': str(image['type']),
            'location': str(image['location']),
        })

    return image_response


"""

Get access Key from Token

"""


def get_access_key(client_id):
    # Currently not yet supported
    return None

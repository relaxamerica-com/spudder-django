from django.http import HttpResponse
from models import APIKeys

import urllib2
import json
import spice_settings

"""

API Landing function

"""

def api_landing(request) :
    return HttpResponse('{"meta":{"error_type":"invalid_entry_point","code":001,"error_message":"Invalid API Entry Point"}}', content_type="application/json")

"""

Validate if API Key is valid

"""

def validate_api_key(api_key) :
    api_key = APIKeys.objects.filter(api_key = api_key, is_active = True)

    if(len(api_key) > 0) :
        return True

    return False

"""

Key Authentication Error JSON String

"""

def key_authentication_error(self) :
    return '{"meta":{"error_type":"invalid_key_error","code":002,"error_message":"Invalid API Key Specified"}}'

"""

Missing Parameters Error JSON String

"""

def missing_parameters_error(self) :
    return '{"meta":{"error_type":"missing_parameters","code":003,"error_message":"API Parameters Missing"}}'

"""

Perform a social media query

"""

def location(request) :

    # Verify if HTTP GET

    json_response = "{}"

    if request.method == 'GET':

        if ('lat' in request.GET and request.GET['lat'] != '') and  \
            ('lat' in request.GET and request.GET['lat'] != '') and \
            ('lat' in request.GET and request.GET['lat'] != '') :

            latitude = request.GET["lat"]
            longitude = request.GET["lon"]
            api_key = request.GET["key"]

            if(validate_api_key(api_key)) :
                # Perform the instagram query
                instagram_request = urllib2.urlopen('https://api.instagram.com/v1/media/search?lat=%s&lng=%s&client_id=%s' % (latitude, longitude, spice_settings.instagram_client_key))

                # Process the JSON returned document
                instagram_response = json.load(instagram_request)
                response_images_data = instagram_response['data']
                image_response = "["

                for image in response_images_data:
                    image_response = image_response + "{ source : 'instagram', "
                    image_response = image_response + " images : " + str(image['images']) + ", "
                    image_response = image_response + " user : " + str(image['user']) + ", "
                    image_response = image_response + " created_time : " + str(image['created_time']) + ", "
                    image_response = image_response + " link : " + str(image['link']) + ", "
                    image_response = image_response + " caption : " + str(image['caption']) + ", "
                    image_response = image_response + " tags : " + str(image['tags']) + ", "
                    image_response = image_response + " type : " + str(image['type']) + ", "
                    image_response = image_response + " location : " + str(image['location'])
                    image_response = image_response + "},"

                image_response = image_response + "]"

                json_response = image_response

            else :
                json_response = key_authentication_error()

        else:
            json_response = missing_parameters_error()

    # Return JSON document
    return HttpResponse(json_response, content_type="application/json")

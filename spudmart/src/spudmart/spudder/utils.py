import settings
import httplib

BASE_HEADERS = {
    "X-Parse-Application-Id": settings.SPUDDER_APPLICATION_ID,
    "X-Parse-REST-API-Key": settings.SPUDDER_REST_API_KEY,
    "Content-Type": "application/json"
}


def get_connection():
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()

    return connection
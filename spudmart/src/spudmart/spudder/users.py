import json
import urllib
from spudmart.spudder.utils import get_connection, BASE_HEADERS


def get_user_data(user):
    user_profile = user.get_profile()
    connection = get_connection()

    params = urllib.urlencode({"where": json.dumps({"amazonID": user_profile.amazon_id})})
    retry = 0
    while retry < 10:
        try:
            connection.request('GET', '/1/users?%s' % params, '', BASE_HEADERS)
            retry = 10
        except Exception:
            retry += 1
    results = json.loads(connection.getresponse().read())['results']

    return results[0] if len(results) else None


def signup_user(user):
    user_profile = user.get_profile()
    connection = get_connection()

    params = json.dumps({
        "username": user.email,
        "password": user_profile.amazon_id,
        "passwordRaw": user_profile.amazon_id,
        "amazonID": user_profile.amazon_id,
        "name": user.username,
        "email": user.email
    })

    retry = 0
    while retry < 10:
        try:
            connection.request('GET', '/1/users', params, BASE_HEADERS)
            retry = 10
        except Exception:
            retry += 1

    json_data = json.loads(connection.getresponse().read())

    return json_data['objectId']


def sign_in_user(user_data):
    connection = get_connection()
    params = urllib.urlencode({
        "username": user_data['username'],
        "password": user_data['passwordRaw']
    })
    connection.request('GET', '/1/login?%s' % params, '', BASE_HEADERS)
    json_data = json.loads(connection.getresponse().read())

    return json_data['sessionToken']


def set_user_is_sponsor(spudder_id, session_token):
    connection = get_connection()

    params = json.dumps({"isSponsor": True})
    headers = BASE_HEADERS
    headers['X-Parse-Session-Token'] = session_token

    connection.request('PUT', '/1/users/%s' % spudder_id, params, headers)
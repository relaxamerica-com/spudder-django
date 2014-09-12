import json
import urllib
from spudmart.spudder.exceptions import UserError, UserErrorCode
from spudmart.spudder.utils import get_connection, BASE_HEADERS, API_RETRY_COUNT


def get_user_data(user):
    user_profile = user.get_profile()
    connection = get_connection()

    params = urllib.urlencode({"where": json.dumps({"amazonID": user_profile.amazon_id})})
    retry = 0
    results = []
    while retry < API_RETRY_COUNT:
        try:
            connection.request('GET', '/1/users?%s' % params, '', BASE_HEADERS)
            results = json.loads(connection.getresponse().read())['results']
            retry = API_RETRY_COUNT
        except Exception:
            retry += 1
            if retry == API_RETRY_COUNT:
                raise UserError(UserErrorCode.GET_USER_DATA_DEADLINE)

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
    json_data = None
    while retry < API_RETRY_COUNT:
        try:
            connection.request('GET', '/1/users', params, BASE_HEADERS)
            json_data = json.loads(connection.getresponse().read())
            retry = API_RETRY_COUNT
        except Exception:
            retry += 1
            if retry == API_RETRY_COUNT:
                raise UserError(UserErrorCode.SIGNUP_USER_DEADLINE)

    return json_data['objectId']


def sign_in_user(user_data):
    connection = get_connection()
    params = urllib.urlencode({
        "username": user_data['username'],
        "password": user_data['passwordRaw']
    })

    retry = 0
    json_data = None
    while retry < API_RETRY_COUNT:
        try:
            connection.request('GET', '/1/login?%s' % params, '', BASE_HEADERS)
            json_data = json.loads(connection.getresponse().read())
            retry = API_RETRY_COUNT
        except Exception:
            retry += 1
            if retry == API_RETRY_COUNT:
                raise UserError(UserErrorCode.SIGN_IN_USER_DEADLINE)

    return json_data['sessionToken']


def set_user_is_sponsor(spudder_id, session_token):
    connection = get_connection()

    params = json.dumps({"isSponsor": True})
    headers = BASE_HEADERS
    headers['X-Parse-Session-Token'] = session_token

    retry = 0
    while retry < API_RETRY_COUNT:
        try:
            connection.request('PUT', '/1/users/%s' % spudder_id, params, headers)
            connection.getresponse()
            retry = API_RETRY_COUNT
        except Exception:
            retry += 1
            if retry == API_RETRY_COUNT:
                raise UserError(UserErrorCode.SET_USER_IS_SPONSOR_DEADLINE)
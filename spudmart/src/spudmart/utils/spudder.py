import settings
import json,httplib

HEADERS = {"X-Parse-Application-Id": settings.SPUDDER_APPLICATION_ID,
           "X-Parse-REST-API-Key": settings.SPUDDER_REST_API_KEY,
           "Content-Type": "application/json"}


def get_team_info(team_id):
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()

    params = json.dumps({"teamID": team_id})
    connection.request('POST', '/1/functions/team', params, HEADERS)
    return json.loads(connection.getresponse().read())['result']


def save_team_recipient(team_id):
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()

    params = json.dumps({"teamID": team_id})
    connection.request('POST', '/1/functions/team_save_recipient', params, HEADERS)

    return connection.getresponse().status == 200
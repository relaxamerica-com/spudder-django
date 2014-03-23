import json
import httplib

import settings
from spudmart.spudder.models import Team, TeamOffer


HEADERS = {"X-Parse-Application-Id": settings.SPUDDER_APPLICATION_ID,
           "X-Parse-REST-API-Key": settings.SPUDDER_REST_API_KEY,
           "Content-Type": "application/json"}


def get_team(team_id):
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()

    connection.request('GET', '/1/classes/Team/%s' % team_id, '', HEADERS)
    json_data = json.loads(connection.getresponse().read())

    team,_ = Team.objects.get_or_create(spudder_id=team_id)
    team.update_from_json(json_data)

    return team


def save_team_is_recipient(team_id):
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()

    params = json.dumps({"isRegisteredRecipient": True})
    connection.request('PUT', '/1/classes/Team/%s' % team_id, params, HEADERS)

    return connection.getresponse().status == 200


def get_offer(offer_id):
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()

    connection.request('GET', '/1/classes/TeamOffer/%s' % offer_id, '', HEADERS)
    json_data = json.loads(connection.getresponse().read())

    team = get_team(json_data['team']['objectId'])
    offer,_ = TeamOffer.objects.get_or_create(spudder_id=offer_id, team=team)
    offer.update_from_json(json_data)

    return offer
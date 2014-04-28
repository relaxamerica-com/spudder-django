import json
from spudmart.spudder.models import Team, TeamOffer
from spudmart.spudder.utils import BASE_HEADERS, get_connection


def get_team(team_id):
    connection = get_connection()

    connection.request('GET', '/1/classes/Team/%s' % team_id, '', BASE_HEADERS)
    json_data = json.loads(connection.getresponse().read())

    team,_ = Team.objects.get_or_create(spudder_id=team_id)
    team.update_from_json(json_data)

    return team


def save_team_is_recipient(team_id):
    connection = get_connection()

    params = json.dumps({"isRegisteredRecipient": True})
    connection.request('PUT', '/1/classes/Team/%s' % team_id, params, BASE_HEADERS)

    return connection.getresponse().status == 200


def get_offer(offer_id):
    connection = get_connection()

    connection.request('GET', '/1/classes/TeamOffer/%s' % offer_id, '', BASE_HEADERS)
    json_data = json.loads(connection.getresponse().read())

    team = get_team(json_data['team']['objectId'])
    offer,_ = TeamOffer.objects.get_or_create(spudder_id=offer_id, team=team)
    offer.update_from_json(json_data)

    return offer
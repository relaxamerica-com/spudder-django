import json
import urllib
from spudmart.spudder.utils import get_connection, BASE_HEADERS


def create_or_update_sponsored_teams(sponsor, team):
    connection = get_connection()
    sponsor_spudder_id = sponsor.get_profile().spudder_id
    sponsor_pointer = {"__type": "Pointer", "className": "_User", "objectId": sponsor_spudder_id}

    params = urllib.urlencode({"where": json.dumps({
        "sponsor": sponsor_pointer
    })})

    retry = 0
    while retry < 10:
        try:
            connection.request('GET', '/1/classes/SponsoredTeams?%s' % params, '', BASE_HEADERS)
            retry = 10
        except Exception:
            retry += 1

    json_data = json.loads(connection.getresponse().read())

    if len(json_data['results']) < 1:
        params = json.dumps({
            "sponsor": sponsor_pointer,
            "teams": {
                "__type": "Relation",
                "className": "Team"
            }
        })

        retry = 0
        while retry < 10:
            try:
                connection.request('POST', '/1/classes/SponsoredTeams', params, BASE_HEADERS)
                retry = 10
            except Exception:
                retry += 1
        entity_spudder_id = json.loads(connection.getresponse().read())['objectId']
    else:
        entity_spudder_id = json.loads(connection.getresponse().read())['results'][0]['objectId']

    params = json.dumps({
        "teams": {
            "__op": "AddRelation",
            "objects": [
                {
                    "__type": "Pointer",
                    "className": "Team",
                    "objectId": team.spudder_id
                }
            ]
        }
    })

    retry = 0
    while retry < 10:
        try:
            connection.request('PUT', '/1/classes/SponsoredTeams/%s' % entity_spudder_id, params, BASE_HEADERS)
            retry = 10
        except Exception:
            retry += 1


def create_or_update_team_sponsors(team, sponsor):
    connection = get_connection()
    sponsor_spudder_id = sponsor.get_profile().spudder_id
    team_pointer = {"__type": "Pointer", "className": "Team", "objectId": team.spudder_id}

    params = urllib.urlencode({"where": json.dumps({
        "team": team_pointer
    })})

    retry = 0
    while retry < 10:
        try:
            connection.request('GET', '/1/classes/TeamSponsors?%s' % params, '', BASE_HEADERS)
            retry = 10
        except Exception:
            retry += 1

    json_data = json.loads(connection.getresponse().read())

    if len(json_data['results']) < 1:
        params = json.dumps({
            "team": team_pointer,
            "sponsors": {
                "__type": "Relation",
                "className": "_User"
            }
        })

        retry = 0
        while retry < 10:
            try:
                connection.request('POST', '/1/classes/TeamSponsors', params, BASE_HEADERS)
                retry = 10
            except Exception:
                retry += 1
        entity_spudder_id = json.loads(connection.getresponse().read())['objectId']
    else:
        entity_spudder_id = json.loads(connection.getresponse().read())['results'][0]['objectId']

    params = json.dumps({
        "sponsors": {
            "__op": "AddRelation",
            "objects": [
                {
                    "__type": "Pointer",
                    "className": "_User",
                    "objectId": sponsor_spudder_id
                }
            ]
        }
    })
    from logging import error
    error('Trying to update Team Sponsors...')
    retry = 0
    while retry < 10:
        try:
            connection.request('PUT', '/1/classes/TeamSponsors/%s' % entity_spudder_id, params, BASE_HEADERS)
            error(connection.getresponse().read())
            retry = 10
        except Exception:
            retry += 1
            error('Retrying for %s time' % retry)
            error(connection.getresponse().read())


def create_or_update_team_offer_sponsors(team, offer, sponsor):
    connection = get_connection()
    sponsor_spudder_id = sponsor.get_profile().spudder_id
    team_pointer = {"__type": "Pointer", "className": "Team", "objectId": team.spudder_id}
    team__offer_pointer = {"__type": "Pointer", "className": "Team", "objectId": offer.spudder_id}

    params = urllib.urlencode({"where": json.dumps({
        "teamOffer": team__offer_pointer
    })})

    retry = 0
    while retry < 10:
        try:
            connection.request('GET', '/1/classes/TeamOfferSponsors?%s' % params, '', BASE_HEADERS)
            retry = 10
        except Exception:
            retry += 1

    json_data = json.loads(connection.getresponse().read())

    if len(json_data['results']) < 1:
        params = json.dumps({
            "teamOffer": team__offer_pointer,
            "team": team_pointer,
            "sponsors": {
                "__type": "Relation",
                "className": "_User"
            }
        })

        retry = 0
        while retry < 10:
            try:
                connection.request('POST', '/1/classes/TeamOfferSponsors', params, BASE_HEADERS)
                retry = 10
            except Exception:
                retry += 1
        entity_spudder_id = json.loads(connection.getresponse().read())['objectId']
    else:
        entity_spudder_id = json.loads(connection.getresponse().read())['results'][0]['objectId']

    params = json.dumps({
        "sponsors": {
            "__op": "AddRelation",
            "objects": [
                {
                    "__type": "Pointer",
                    "className": "_User",
                    "objectId": sponsor_spudder_id
                }
            ]
        }
    })

    from logging import error
    error('Trying to update Team Offer Sponsors...')
    retry = 0
    while retry < 10:
        try:
            connection.request('PUT', '/1/classes/TeamOfferSponsors/%s' % entity_spudder_id, params, BASE_HEADERS)
            error(connection.getresponse().read())
            retry = 10
        except Exception:
            retry += 1
            error('Retrying for %s time' % retry)
            error(connection.getresponse().read())
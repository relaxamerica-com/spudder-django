import json
import urllib
from spudmart.spudder.exceptions import SponsorshipSynchronizationError, SponsorshipSynchronizationErrorCode
from spudmart.spudder.utils import get_connection, BASE_HEADERS, API_RETRY_COUNT


def create_or_update_sponsored_teams(sponsor, team):
    connection = get_connection()
    sponsor_spudder_id = sponsor.get_profile().spudder_id
    sponsor_pointer = {"__type": "Pointer", "className": "_User", "objectId": sponsor_spudder_id}

    params = urllib.urlencode({"where": json.dumps({
        "sponsor": sponsor_pointer
    })})

    retry = 0
    query_json_data = None
    entity_spudder_id = None

    while retry < API_RETRY_COUNT:
        try:
            connection.request('GET', '/1/classes/SponsoredTeams?%s' % params, '', BASE_HEADERS)
            query_response = connection.getresponse()
            query_json_data = json.loads(query_response.read())
            retry = API_RETRY_COUNT
        except Exception:
            retry += 1
            if retry == API_RETRY_COUNT:
                raise SponsorshipSynchronizationError(SponsorshipSynchronizationErrorCode.ST_QUERY_DEADLINE)

    if len(query_json_data['results']) < 1:
        params = json.dumps({
            "sponsor": sponsor_pointer,
            "teams": {
                "__type": "Relation",
                "className": "Team"
            }
        })

        retry = 0
        while retry < API_RETRY_COUNT:
            try:
                connection.request('POST', '/1/classes/SponsoredTeams', params, BASE_HEADERS)
                creation_response = connection.getresponse()
                entity_spudder_id = json.loads(creation_response.read())['objectId']
                retry = API_RETRY_COUNT
            except Exception:
                if retry == API_RETRY_COUNT:
                    raise SponsorshipSynchronizationError(SponsorshipSynchronizationErrorCode.ST_CREATION_DEADLINE)
    else:
        entity_spudder_id = query_json_data['results'][0]['objectId']

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
    while retry < API_RETRY_COUNT:
        try:
            connection.request('PUT', '/1/classes/SponsoredTeams/%s' % entity_spudder_id, params, BASE_HEADERS)
            connection.getresponse()
            retry = API_RETRY_COUNT
        except Exception:
            retry += 1
            if retry == API_RETRY_COUNT:
                raise SponsorshipSynchronizationError(SponsorshipSynchronizationErrorCode.ST_RELATION_ADD_DEADLINE)


def create_or_update_team_sponsors(team, sponsor):
    connection = get_connection()
    sponsor_spudder_id = sponsor.get_profile().spudder_id
    team_pointer = {"__type": "Pointer", "className": "Team", "objectId": team.spudder_id}

    params = urllib.urlencode({"where": json.dumps({
        "team": team_pointer
    })})

    retry = 0
    query_json_data = None
    while retry < API_RETRY_COUNT:
        try:
            connection.request('GET', '/1/classes/TeamSponsors?%s' % params, '', BASE_HEADERS)
            query_response = connection.getresponse()
            query_json_data = json.loads(query_response.read())
            retry = API_RETRY_COUNT
        except Exception, e:
            retry += 1
            if retry == API_RETRY_COUNT:
                raise SponsorshipSynchronizationError(SponsorshipSynchronizationErrorCode.TS_QUERY_DEADLINE)

    entity_spudder_id = None
    if len(query_json_data['results']) < 1:
        params = json.dumps({
            "team": team_pointer,
            "sponsors": {
                "__type": "Relation",
                "className": "_User"
            }
        })

        retry = 0
        while retry < API_RETRY_COUNT:
            try:
                connection.request('POST', '/1/classes/TeamSponsors', params, BASE_HEADERS)
                creation_getresponse = connection.getresponse()
                entity_spudder_id = json.loads(creation_getresponse.read())['objectId']
                retry = API_RETRY_COUNT
            except Exception:
                retry += 1
                if retry == API_RETRY_COUNT:
                    raise SponsorshipSynchronizationError(SponsorshipSynchronizationErrorCode.TS_CREATION_DEADLINE)
    else:
        entity_spudder_id = query_json_data['results'][0]['objectId']

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

    retry = 0
    while retry < API_RETRY_COUNT:
        try:
            connection.request('PUT', '/1/classes/TeamSponsors/%s' % entity_spudder_id, params, BASE_HEADERS)
            connection.getresponse()
            retry = API_RETRY_COUNT
        except Exception:
            retry += 1
            if retry == API_RETRY_COUNT:
                raise SponsorshipSynchronizationError(SponsorshipSynchronizationErrorCode.TS_RELATION_ADD_DEADLINE)

def create_or_update_team_offer_sponsors(team, offer, sponsor):
    connection = get_connection()
    sponsor_spudder_id = sponsor.get_profile().spudder_id
    team_pointer = {"__type": "Pointer", "className": "Team", "objectId": team.spudder_id}
    team__offer_pointer = {"__type": "Pointer", "className": "TeamOffer", "objectId": offer.spudder_id}

    params = urllib.urlencode({"where": json.dumps({
        "teamOffer": team__offer_pointer
    })})

    retry = 0
    query_json_data = None
    entity_spudder_id = None

    while retry < API_RETRY_COUNT:
        try:
            connection.request('GET', '/1/classes/TeamOfferSponsors?%s' % params, '', BASE_HEADERS)
            query_response = connection.getresponse()
            query_json_data = json.loads(query_response.read())
            retry = API_RETRY_COUNT
        except Exception:
            retry += 1
            if retry == API_RETRY_COUNT:
                raise SponsorshipSynchronizationError(SponsorshipSynchronizationErrorCode.TOS_QUERY_DEADLINE)

    if len(query_json_data['results']) < 1:
        params = json.dumps({
            "teamOffer": team__offer_pointer,
            "team": team_pointer,
            "sponsors": {
                "__type": "Relation",
                "className": "_User"
            }
        })

        retry = 0
        while retry < API_RETRY_COUNT:
            try:
                connection.request('POST', '/1/classes/TeamOfferSponsors', params, BASE_HEADERS)
                entity_spudder_id = json.loads(connection.getresponse().read())['objectId']
                retry = API_RETRY_COUNT
            except Exception:
                retry += 1
                if retry == API_RETRY_COUNT:
                    raise SponsorshipSynchronizationError(SponsorshipSynchronizationErrorCode.TOS_CREATION_DEADLINE)

    else:
        entity_spudder_id = query_json_data['results'][0]['objectId']

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

    retry = 0
    while retry < API_RETRY_COUNT:
        try:
            connection.request('PUT', '/1/classes/TeamOfferSponsors/%s' % entity_spudder_id, params, BASE_HEADERS)
            connection.getresponse()
            retry = API_RETRY_COUNT
        except Exception:
            retry += 1
            if retry == API_RETRY_COUNT:
                    raise SponsorshipSynchronizationError(SponsorshipSynchronizationErrorCode.TOS_RELATION_ADD_DEADLINE)


def decrement_team_offer_available_quantity(offer):
    connection = get_connection()
    offer_id = offer.spudder_id

    params = json.dumps({"quantityAvailable": {"__op": "Increment", "amount": -1}})
    retry = 0
    while retry < API_RETRY_COUNT:
        try:
            connection.request('PUT', '/1/classes/TeamOffer/%s' % offer_id, params, BASE_HEADERS)
            connection.getresponse()
            retry = API_RETRY_COUNT
        except Exception:
            retry += 1
            if retry == API_RETRY_COUNT:
                raise SponsorshipSynchronizationError(SponsorshipSynchronizationErrorCode.TO_AVAILABLE_QUANTITY_DECREMENT_DEADLINE)
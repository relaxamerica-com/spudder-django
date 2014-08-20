import urllib
from google.appengine.api import urlfetch
import settings
import simplejson
import time
import logging
from spudderdomain.models import TeamPage
from spudderkrowdio.models import KrowdIOStorage
from spudmart.venues.models import Venue


def _update_entity(entity, krowdio_data):
    entity.krowdio_access_token = krowdio_data['access_token']
    entity.krowdio_access_token_expires = krowdio_data['expires_in']
    entity.krowdio_user_id = krowdio_data['user']['_id']
    entity.krowdio_email = '%s@spudder.com' % krowdio_data['user']['username']
    entity.save()


def _get(url, data, headers={}):
    result = urlfetch.fetch(url=url, headers=headers)
    if result.status_code == 200:
        return result
    else:
        raise Exception('GET result status code different than 200: %s' % result.content)


def _post(url, data, headers={}):
    data = urllib.urlencode(data)
    result = urlfetch.fetch(url=url,
                            payload=data,
                            method=urlfetch.POST,
                            headers=headers)
    if result.status_code == 200:
        return result
    else:
        raise Exception('POST result status code different than 200: %s' % result.content)


def _delete(url, data, headers={}):
    data = urllib.urlencode(data)
    result = urlfetch.fetch(url=url,
                            payload=data,
                            method=urlfetch.DELETE,
                            headers=headers)
    return result
    
    
def _ensure_oAuth_token(entity):
    expires = entity.krowdio_access_token_expires
    seconds = int(round(time.time()))
    
    if seconds > expires + 10:
        data = {
            'client_id': settings.KROWDIO_CLIENT_KEY,
            'email': entity.krowdio_email,
            'password': settings.KROWDIO_GLOBAL_PASSWORD
        }
        response = _post('http://auth.krowd.io/user/login', data)
        krowdio_data = simplejson.loads(response.content)
        
        _update_entity(entity, krowdio_data)
    
    return 'Token token="' + entity.krowdio_access_token + '"'
    
        
def post_spud(entity, data):
    token = _ensure_oAuth_token(entity)
    
    logging.info(token)
    
    logging.info(_post('http://api.krowd.io/post', data, { 'Authorization' : token }))
    

def delete_spud(entity, spud_id):
    token = _ensure_oAuth_token(entity)
    
    _delete('http://api.krowd.io/post/%s' % spud_id, {}, { 'Authorization' : token })
    

def get_spuds_for_entity(entity, page=1):
    token = _ensure_oAuth_token(entity)
    
    response = _get('http://api.krowd.io/stream/%s?limit=10&page=%s' % (entity.krowdio_user_id, str(page)), {}, { 'Authorization' : token })
    
    return simplejson.loads(response.content)


def get_user_mentions_activity(entity):
    token = _ensure_oAuth_token(entity)
    
    user_id = entity.krowdio_user_id
    
    response = _get('http://api.krowd.io/activity/mentions?userid=%s' % user_id, {}, {'Authorization': token})

    response = simplejson.loads(response.content)

    items = response.get('items', [])

    return [i.get('target', {}).get('json', {}).get('extra', {}) for i in items]


def post_comment(entity, spud_id, text):
    token = _ensure_oAuth_token(entity)
    
    data = {
        'text' : text
    }
    
    _post('http://api.krowd.io/comment/%s' % spud_id, data, { 'Authorization' : token })
    
    
def like_spud(entity, spud_id):
    token = _ensure_oAuth_token(entity)
    
    _post('http://api.krowd.io/like/%s' % spud_id, {}, { 'Authorization' : token })
    

def get_spud_likes(entity, spud_id, page=1):
    token = _ensure_oAuth_token(entity)
    
    response = _get('http://api.krowd.io/like/%s?limit=5&page=%s&newpage=1&startid=&direction=None' % (spud_id, str(page)), {}, { 'Authorization' : token })
    
    return simplejson.loads(response.content)


def get_spud_comments(entity, spud_id, page=1):
    token = _ensure_oAuth_token(entity)
    
    response = _get('http://api.krowd.io/comment/%s?limit=5&page=%s&newpage=1&startid=&direction=None' % (spud_id, str(page)), {}, { 'Authorization' : token })
    
    return simplejson.loads(response.content)


def start_following(current_role, entity_type, entity_id):
    """
    Adds a KrowdIO User to a Fan's followers
    :param current_role: any Role<Type> object (the Fan)
    :param entity_type: a KrowdIOStorage type string ('Venue', 'Team',
        or 'fan')
    :param entity_id: the ID of the original object to be followed (the
        Venue id, the Team id, or the Fan id)
    :return: the json response from the KrowdIO API
    """
    entity = KrowdIOStorage.GetOrCreateForCurrentUserRole(user_role=current_role)
    token = _ensure_oAuth_token(entity)

    following_id = None
    if entity_type == 'Venue':
        following_id = KrowdIOStorage.GetOrCreateForVenue(entity_id).krowdio_user_id
    elif entity_type == 'Team':
        following_id = KrowdIOStorage.GetOrCreateForTeam(entity_id).krowdio_user_id
    elif entity_type == 'fan':
        following_id = KrowdIOStorage.GetOrCreateFromRoleEntity(entity_id, entity_type).krowdio_user_id

    response = _post(
        'http://api.krowd.io/user/%s/relationship' % following_id,
        {'action': 'follow'},
        {'Authorization': token})

    return simplejson.loads(response.content)


def stop_following(current_role, entity_type, entity_id):
    """
    Removes a KrowdIO User from a Fan's followers
    :param current_role: any Role<Type> object (the Fan)
    :param entity_type: a KrowdIOStorage type string ('Venue' or value
        in RoleController.ENTITY_TYPES)
    :param entity_id: the ID of the original object followed (the Venue
        id, the Team id, or the Fan id)
    :return: the json response from the KrowdIO API
    """
    entity = KrowdIOStorage.GetOrCreateForCurrentUserRole(user_role=current_role)
    token = _ensure_oAuth_token(entity)

    following_id = None
    if entity_type == 'Venue':
        ven = Venue.objects.get(id=entity_id)
        following_id = KrowdIOStorage.objects.get(venue=ven).krowdio_user_id
    elif entity_type == 'Team':
        team = TeamPage.objects.get(id=entity_id)
        following_id = KrowdIOStorage.objects.get(team=team).krowdio_user_id
    elif entity_type is 'fan':
        following_id = KrowdIOStorage.objects.get(role_id=entity_id).krowdio_user_id

    response = _post(
        'http://api.krowd.io/user/%s/relationship' % following_id,
        {'action': 'unfollow'},
        {'Authorization': token})

    return simplejson.loads(response.content)


def get_following(current_role):
    """
    Gets KrowdIO users that a Fan is following
    :param current_role: any Role<Type> object (a Fan)
    :return: the json response from the KrowdIO API
    """
    entity = KrowdIOStorage.GetOrCreateForCurrentUserRole(user_role=current_role)
    token = _ensure_oAuth_token(entity)

    response = _get(
        'http://api.krowd.io/user/%s/following' % entity.krowdio_user_id,
        {},
        {'Authorization': token})

    return simplejson.loads(response.content)
import urllib
from google.appengine.api import urlfetch
import settings
import simplejson
import time
import logging


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
    

def register_entity(entity):
    data = {
        'client_id': settings.KROWDIO_CLIENT_KEY,
        'username':  entity.type + str(entity._id),
        'email': entity.type + str(entity._id) + "@spudder.com",
        'password': settings.KROWDIO_GLOBAL_PASSWORD
    }
    
    response = _post('http://auth.krowd.io/user/register', data)
    krowdio_data = simplejson.loads(response.content)
    
    _update_entity(entity, krowdio_data)
    
    
def _update_entity(entity, krowdio_data):
    entity.krowdio_access_token = krowdio_data['access_token']
    entity.krowdio_access_token_expires = krowdio_data['expires_in']
    entity.krowdio_user_id = krowdio_data['user']['_id']
    entity.krowdio_email = '%s@spudder.com' % krowdio_data['user']['username']
    entity.save()
    
    
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
    
    response = _get('http://api.krowd.io/activity/mentions?userid=%s' % (user_id), {}, { 'Authorization' : token })
    
    return simplejson.loads(response.content)


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

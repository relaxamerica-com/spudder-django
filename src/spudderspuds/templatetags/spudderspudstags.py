import re
import json
from django.core.exceptions import ObjectDoesNotExist
from google.appengine.api import urlfetch
from django.template.defaulttags import register
from spudderdomain.controllers import RoleController, EntityController
from spudderdomain.models import FanPage
from spudderkrowdio.models import KrowdIOStorage, FanFollowingEntityTag
from spudmart.CERN.models import STATES, Student
from spudmart.accounts.templatetags.accounts import fan_page_name, user_name


@register.simple_tag
def link_to_twitter_profile(twitter_username):
    return 'http://twitter.com/%s' % ((twitter_username or '').replace('@', ''))


@register.simple_tag
def link_to_instagram_profile(twitter_username):
    return 'http://instagram.com/%s' % ((twitter_username or '').replace('@', ''))


@register.filter
def format_state(state):
    if not state or state not in STATES.keys():
        return 'Not set'
    return STATES[state]


@register.filter
def get_protected_id(krowdio_dict):
    """
    Gets the _id property of a krowdio dict
    :param krowdio_dict: a json object from the KrowdIO API
    :return: a string of the _id property
    """
    return krowdio_dict['_id']


@register.simple_tag()
def get_team_admin_name(team_admin):
    """
    Gets name for the entity of TeamAdministrator object
    :param team_admin: any TeamAdmininstrator object
    :return: a name as string
    """
    if team_admin.entity_type == 'fan':
        return fan_page_name(FanPage.objects.get(id=team_admin.entity_id))
    elif team_admin.entity_type == 'student':
        return user_name(Student.objects.get(id=team_admin.entity_id).user)

@register.simple_tag()
def get_team_admin_profile(team_admin):
    """
    Rel link to entity of TeamAdministrator object
    :param team_admin: any TeamAdministrator object
    :return: a rel link to profile
    """
    if team_admin.entity_type == 'fan':
        return '/fan/%s' % team_admin.entity_id
    elif team_admin.entity_type == 'student':
        return '/cern/student/%s' % team_admin.entity_id
    else:
        return '/'


@register.simple_tag
def entity_static_button(entity_type, size='small'):
    if entity_type == "team":
        return '/static/img/spudderspuds/button-teams-%s.png' % size
    elif entity_type == "fan":
        return '/static/img/spudderspuds/button-fans-%s.png' % size
    elif entity_type == "venue":
        return '/static/img/spuddervenues/button-venues-%s.png' % size

@register.simple_tag
def entity_button(entity, entity_type, size='small'):
    if entity_type == "team":
        if entity.image:
            return '/file/serve/%s' % entity.image.id
        else:
            return '/static/img/spudderspuds/button-teams-%s.png' % size
    elif entity_type == "fan":
        if entity.avatar:
            return '/file/serve/%s' % entity.avatar.id
        else:
            return '/static/img/spudderspuds/button-fans-%s.png' % size
    elif entity_type == "venue":
        if entity.logo:
            return '/file/serve/%s' % entity.logo.id
        else:
            return '/static/img/spuddervenues/button-venues-%s.png' % size


@register.simple_tag
def entity_view_link(entity, entity_type):
    if entity_type == "venue":
        return '/venues/view/%s' % entity.id
    else:
        return '/%s/%s' % (entity_type, entity.id)


@register.inclusion_tag('components/social_media_list.html')
def social_media_list(entity):
    return {'entity ': entity}


@register.filter
def spud_is_valid(spud):
    if not spud or not spud.get('image'):
        return False
    if not spud.get('image', {}).get('standard_resolution'):
        return False
    if not spud.get('image', {}).get('standard_resolution', {}).get('url'):
        return False
    try:
        result = urlfetch.fetch(url=spud['image']['standard_resolution']['url'])
        if result.status_code == 404:
            return False
        return True
    except:
        return False


@register.simple_tag
def krowdio_user_profile(krowdio_user):
    """
    Links to the Spudder profile from KrowdIO user ID
    :param krowdio_user: a User description from KrowdIO API
    :return: a rel link to a Spudder profile page
    """
    storage = KrowdIOStorage.objects.get(krowdio_user_id=krowdio_user['_id'])
    return get_link_from_storage(storage)


def get_link_from_storage(storage):
    """
    Gets a rel link to profile from a KrowdIO storage object
    :param storage: any KrowdIO Storage object
    :return: a string rel link to Spudder profile
    """
    if storage.role_type == RoleController.ENTITY_FAN:
        return '/fan/%s' % storage.role_id
    elif storage.role_type == EntityController.ENTITY_TEAM:
        return '/team/%s' % storage.team.id
    elif storage.role_type == EntityController.ENTITY_VENUE:
        return '/venues/view/%s' % storage.venue.id


@register.filter
def parse_text_for_entities(user_mentions, krowdio_user):
    """
    Makes tagged entities into links
    :param user_mentions: the users linked to a SPUD
    :param krowdio_user: the SPUD author
    :return: html of image by type & links to profiles
    """
    poster = KrowdIOStorage.objects.get(krowdio_user_id=krowdio_user['_id'])
    mentioned = []
    links = []
    for user in user_mentions:
        storage = KrowdIOStorage.objects.get(krowdio_user_id=user['_id'])
        if storage != poster and storage not in mentioned:
            link = get_link_from_storage(storage)
            img = "/static/img/spudderspuds/button-spuds-tiny.png"
            name = ""
            if storage.role_type == RoleController.ENTITY_FAN:
                img = "/static/img/spudderspuds/button-fans-tiny.png"
                name = "Fan: %s" % FanPage.objects.get(id=storage.role_id).name
            elif storage.role_type == EntityController.ENTITY_TEAM:
                img = "/static/img/spudderspuds/button-teams-tiny.png"
                name = "Team: %s" % storage.team.name
            elif storage.role_type == EntityController.ENTITY_VENUE:
                img = "/static/img/spuddervenues/button-venues-tiny.png"
                name = "Venue: %s" % storage.venue.aka_name
            links.append('<a href="%s" title="%s"><img src="%s"></a>' % (link, name, img))
            mentioned.append(storage)

    return ' '.join(links)


@register.filter
def get_all_user_mentions(full_spud):
    """
    Pulls user mentions from original posts & comments
    :param full_spud: a SPUD fresh from KrowdIO API
    :return: a list of dicts of user_mentions
    """
    user_mentions = full_spud['entities']['user_mentions']
    if len(full_spud['comments']) > 1:
        for comment in full_spud['comments']['data']:
            user_mentions += comment['entities']['user_mentions']

    return user_mentions

@register.filter('jsonify')
def jsonify(obj):
    if obj and hasattr(obj, 'as_json'):
        return obj.as_json()
    return json.dumps(obj or {})



from django.template.defaulttags import register
from spudderdomain.models import FanPage
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
        if entity.image:
            return '/file/serve/%s' % entity.image.id
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
    return {'entity': entity}
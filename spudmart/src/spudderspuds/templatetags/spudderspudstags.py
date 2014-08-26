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
from django.template.defaulttags import register
from spudmart.CERN.models import STATES


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
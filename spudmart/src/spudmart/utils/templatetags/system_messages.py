from django import template
from spudmart.utils.system_messages import get_messages_for_user

register = template.Library()


@register.inclusion_tag('utils/system_messages.html')
def display_messages_for_user(user):
    return {'messages': get_messages_for_user(user)}
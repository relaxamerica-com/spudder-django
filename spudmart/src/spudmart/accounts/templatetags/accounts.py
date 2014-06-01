from django import template
from django.contrib.auth.models import SiteProfileNotAvailable

register = template.Library()

@register.simple_tag
def user_name(user):
    try:
        profile = user.get_profile()
        return profile.username
    except SiteProfileNotAvailable:
        return user.username
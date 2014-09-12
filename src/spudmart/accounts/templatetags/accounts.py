from django import template
from django.contrib.auth.models import SiteProfileNotAvailable
from spudmart.accounts.utils import is_student as is_student_util, \
    is_sponsor as is_sponsor_util

register = template.Library()


@register.simple_tag
def user_name(user):
    if user.first_name or user.last_name:
        return "%s %s" % (user.first_name, user.last_name)
    else:
        return 'No Name (%s)' % user.email


@register.filter
def is_student(user):
    """
    Determines if user relates to a Student

    :param user: any authenticated user
    :return: boolean of whether user relates to a Student object
    """
    return is_student_util(user)

@register.filter
def is_sponsor(user):
    """
    Determines if the user is a sponsor

    :param user: any authenticated user
    :return: boolean whether user is sponsor
    """
    return is_sponsor_util(user)


@register.simple_tag()
def fan_page_name(fan_page):
    """
    Gets the display name for a fan page
    :param fan_page: any FanPage object
    :return: a name as str
    """
    return fan_page.name or 'No Name'
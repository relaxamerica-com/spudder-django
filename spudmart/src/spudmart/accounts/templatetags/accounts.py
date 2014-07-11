from django import template
from django.contrib.auth.models import SiteProfileNotAvailable
from spudmart.accounts.utils import is_student as is_student_util, \
    is_sponsor as is_sponsor_util

register = template.Library()


@register.simple_tag
def user_name(user):
    try:
        return str(user.first_name) + " " + str(user.last_name)
    except Exception:
        return ''


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
from django import template
from django.contrib.auth.models import SiteProfileNotAvailable
from spudmart.accounts.utils import is_student as is_student_util

register = template.Library()


@register.simple_tag
def user_name(user):
    try:
        profile = user.get_profile()
        return profile.username
    except SiteProfileNotAvailable:
        return user.username
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
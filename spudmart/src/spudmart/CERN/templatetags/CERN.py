from django import template
from spudmart.CERN.utils import strip_invalid_chars
register = template.Library()


@register.simple_tag
def strip_school_name(school):
    """
    Strips invalid characters from the school name for nicer URLs
    :param school: a School object whose name we want stripped
    :return: the name of the school without any invalid characters
    """
    return strip_invalid_chars(school.name)
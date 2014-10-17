from django.template.defaulttags import register
from spudderdomain.utils import is_feature_enabled


@register.filter()
def feature_is_enabled(feature):
    enabled = is_feature_enabled(feature)
    return enabled

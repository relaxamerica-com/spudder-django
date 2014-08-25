from django.conf import settings
from django.template.defaulttags import register


@register.filter()
def feature_is_enabled(feature):
    return feature in settings.FEATURES[settings.ENVIRONMENT]

import logging
from django.conf import settings
from django.template.defaulttags import register


@register.filter()
def feature_is_enabled(feature):
    enabled = bool(feature in settings.FEATURES[settings.ENVIRONMENT])
    # logging.error("%s - %s - %s" % (feature, settings.ENVIRONMENT, enabled))
    return enabled

@register.simple_tag()
def environ_features(feature):
    return settings.FEATURES[settings.ENVIRONMENT]



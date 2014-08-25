from django.conf import settings
from django.template.defaulttags import register


@register.simple_tag(takes_context=True)
def feature_is_enabled(context, feature):
    return feature in settings.FEATURES[settings.ENVIRONMENT]

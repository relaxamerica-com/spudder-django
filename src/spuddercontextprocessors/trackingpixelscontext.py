from django.conf import settings
from django.shortcuts import render
from spudderadmin.templatetags.featuretags import feature_is_enabled


def tracking_pixel_code(request):
    """
    Looks for a TRACKING_PIXEL_CONF dict in the setting file
    and if the event (dict key) has a list of template names
    then these are added to the context as {{ tracking_pixel_code }}
    """
    tracking_pixel_code = ""
    if feature_is_enabled('tracking_pixels'):
        for event in request.events:
            templates = settings.TRACKING_PIXEL_CONF.get(event, [])
            for template in templates:
                tracking_pixel_code += render(request, template, {})

    return {'tracking_pixel_code': tracking_pixel_code}

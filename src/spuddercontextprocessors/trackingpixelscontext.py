from django.template.context import RequestContext
from django.template.loader import render_to_string
from events import TRACKING_PIXEL_CONF
from spudderadmin.templatetags.featuretags import feature_is_enabled
from spuddermiddleware.spuddereventsmiddleware import EventsMiddleware


def tracking_pixel_code_context(request):
    """
    Looks for a TRACKING_PIXEL_CONF dict in the events file
    and if the event (dict key) has a list of template names
    then these are added to the context as {{ tracking_pixel_code }}
    """
    tracking_pixel_code = ""
    if feature_is_enabled('tracking_pixels'):
        events = request.session.pop(EventsMiddleware.EVENTS_KEY_NAME, [])
        for event in events:
            templates = TRACKING_PIXEL_CONF.get(event, [])
            context_instance = RequestContext(request, {})
            for template in templates:
                tracking_pixel_code += render_to_string(template, context_instance=context_instance)

    return {'tracking_pixel_code': tracking_pixel_code}

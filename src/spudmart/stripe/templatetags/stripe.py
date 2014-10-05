from django.core.exceptions import ImproperlyConfigured
from django import template
import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def authorize_url(context):
    if not 'request' in context:
        raise ImproperlyConfigured

    authorize_url = 'https://connect.stripe.com/oauth/authorize?response_type=code'
    authorize_url += '&client_id=%s' % settings.STRIPE_CLIENT_ID

    if context['request'].META['SERVER_NAME'] in ['localhost', 'testserver']:
        redirect_uri = 'http://localhost:9191'
    else:
        redirect_uri = settings.SPUDMART_BASE_URL
    redirect_uri += '/club/stripe'
    authorize_url += '&redirect_uri=%s' % redirect_uri
    authorize_url += '&scope=read_write'

    return authorize_url
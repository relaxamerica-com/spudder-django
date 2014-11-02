import json
from simplejson import JSONDecodeError

from spudderdomain.models import StripeUser, StripeRecipient
from spudderstripe.controllers import StripeController


def get_stripe_recipient_controller_for_club(club):
    try:
        stripe_user = StripeUser.objects.get(club=club)
    except StripeUser.DoesNotExist:
        return None

    return StripeController(stripe_user)


def parse_webhook_request(request):
    # noinspection PyBroadException
    try:
        return json.loads(request.raw_post_data)
    except JSONDecodeError:
        return None
    except ValueError:
        return None
    except Exception:
        return None


def get_event_attribute(event_json, attribute):
    try:
        return event_json[attribute]
    except KeyError:
        return None


class StripeOAuthError():
    def __init__(self):
        pass

    ACCESS_DENIED = 'access_denied'


def get_oauth_request_error(request):
    if not 'error' in request.GET:
        return None

    # We only care about access_denied error as for now it's the only error that result in web browser redirect
    # Reference: https://stripe.com/docs/connect/reference ("Error Response" section)
    if request.GET.get('error', '') == StripeOAuthError.ACCESS_DENIED:
        return StripeOAuthError.ACCESS_DENIED

    return None
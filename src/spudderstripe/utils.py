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
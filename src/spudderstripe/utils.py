import json
from spudderdomain.models import StripeUser, StripeRecipient
from spudderstripe.controllers import StripeRecipientsController


def get_stripe_recipient_controller_for_club(club):
    try:
        stripe_recipient = StripeRecipient.objects.get(club=club)
    except StripeRecipient.DoesNotExist:
        return None
    try:
        stripe_user = StripeUser.objects.get(club=club)
    except StripeUser.DoesNotExist:
        return None
    return StripeRecipientsController(stripe_recipient, stripe_user)


def parse_webhook_request(request):
    try:
        return json.loads(request.raw_post_data)
    except ValueError:
        return None


def get_event_attribute(event_json, attribute):
    try:
        return event_json[attribute]
    except KeyError:
        return None
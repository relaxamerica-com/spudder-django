from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from spudderdomain.models import ChallengeParticipation
from spudderspuds.challenges.utils import challenge_state_engine, _StateEngineStates
from spudderstripe.utils import parse_webhook_request, get_event_attribute


class CardChargeEvents():
    def __init__(self):
        pass

    SUCCEEDED = 'charge.succeeded'
    FAILED = 'charge.failed'

    @staticmethod
    def get_available_events():
        return [CardChargeEvents.SUCCEEDED, CardChargeEvents.FAILED]

    @staticmethod
    def if_valid_event(event):
        return event in CardChargeEvents.get_available_events()


@require_POST
@csrf_exempt
def webhook(request):
    event_json = parse_webhook_request(request)
    event_type = get_event_attribute(event_json, 'type')

    if event_type is None or not CardChargeEvents.if_valid_event(event_type):
        return HttpResponse()  # at this point we only care if payment for challenge pledge was successful or not

    if event_type == CardChargeEvents.SUCCEEDED:
        return HttpResponse()  # Although this event tells us that the charge was successful we don't do anything - we already assumed that it will succeed

    charge_id = get_event_attribute(event_json, 'id')
    if charge_id is None:
        return HttpResponse()  # we don't care for invalid webhook requests

    try:
        challenge_participation = ChallengeParticipation.objects.get(charge_id=charge_id)
        challenge = challenge_participation.challenge
    except ChallengeParticipation.DoesNotExist:
        # All instances (not only the current one) can receive webhook. That's why we need to ensure that challenge
        # participation was made here. If not, just disregard the event.
        return HttpResponse()

    fake_request = {
        'method': 'GET',
        'current_role': {
            'entity': {
                'id': challenge_participation.participating_entity_id
            },
            'entity_type': challenge_participation.participating_entity_type
        }
    }

    challenge_state_engine(fake_request, challenge, None, _StateEngineStates.PAY_FAILED)

    return HttpResponse()
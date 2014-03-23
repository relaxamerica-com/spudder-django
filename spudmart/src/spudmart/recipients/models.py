from django.db import models
from spudmart.spudder.models import Team
from django.contrib.auth.models import User


class RecipientRegistrationState():
    def __init__(self):
        pass

    NOT_STARTED = 1
    FINISHED = 2
    TERMINATED = 3


class RecipientRegistrationStatus():
    def __init__(self):
        pass

    SUCCESS = 'Success'
    A = 'A'
    CE = 'CE'
    NP = 'NP'
    NM = 'NM'
    SPUDDER_SAVE_FAILED = 'SPUDDER_SAVE_FAILED'

    @staticmethod
    def get_from_code(status_code):
        if status_code == 'A':
            return RecipientRegistrationStatus.A
        if status_code == 'CE':
            return RecipientRegistrationStatus.CE
        if status_code == 'NP':
            return RecipientRegistrationStatus.NP
        if status_code == 'NM':
            return RecipientRegistrationStatus.NM

        return RecipientRegistrationStatus.SUCCESS

    @staticmethod
    def get_status_message(status):
        if RecipientRegistrationStatus.A == status:
            return 'Pipeline has been aborted by the user.'
        if RecipientRegistrationStatus.CE == status:
            return 'Caller exception'
        if RecipientRegistrationStatus.NP == status:
            return 'Pipeline problem'
        if RecipientRegistrationStatus.NM == status:
            return 'You are not registered as a third-party caller to make this transaction. Contact Amazon Payments for more information.'
        if RecipientRegistrationStatus.SPUDDER_SAVE_FAILED == status:
            return 'Error while saving information on Spudder. Please try again.'

        return 'Success'


class Recipient(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    team = models.ForeignKey(Team)
    recipient_token_id = models.CharField()
    refund_token_id = models.CharField()
    state = models.IntegerField(default=RecipientRegistrationState.NOT_STARTED)
    status_code = models.CharField()
    registered_by = models.ForeignKey(User)
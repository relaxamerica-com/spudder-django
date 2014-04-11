from django.db import models
from spudmart.spudder.models import Team
from django.contrib.auth.models import User


class RecipientRegistrationState():
    def __init__(self):
        pass

    NOT_STARTED = 1
    FINISHED = 2
    TERMINATED = 3


class Recipient(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    team = models.ForeignKey(Team)
    recipient_token_id = models.CharField()
    refund_token_id = models.CharField()
    state = models.IntegerField(default=RecipientRegistrationState.NOT_STARTED)
    status_code = models.CharField()
    registered_by = models.ForeignKey(User)
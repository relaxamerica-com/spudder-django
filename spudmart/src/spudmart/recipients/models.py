from django.db import models
from spudmart.spudder.models import Team
from django.contrib.auth.models import User


class RecipientRegistrationState():
    def __init__(self):
        pass

    NOT_STARTED = 1
    FINISHED = 2
    TERMINATED = 3

class AmazonRecipient(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    recipient_token_id = models.CharField(max_length=255)
    refund_token_id = models.CharField(max_length=255)
    state = models.IntegerField(default=RecipientRegistrationState.NOT_STARTED)
    status_code = models.CharField(max_length=255)
    
    class Meta:
        abstract = True

class Recipient(AmazonRecipient):
    registered_by = models.ForeignKey(User)
    team = models.ForeignKey(Team)
    pass

class VenueRecipient(AmazonRecipient):
    groundskeeper = models.ForeignKey(User)
    pass
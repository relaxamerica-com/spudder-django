from django.contrib.auth.models import User
from django.db import models
from spudmart.spudder.models import TeamOffer
from spudmart.venues.models import Venue


class DonationState():
    def __init__(self):
        pass

    NOT_STARTED = 1
    PENDING = 2
    FINISHED = 3
    TERMINATED = 4


class AmazonPayment(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    donor = models.ForeignKey(User)
    donation = models.FloatField(default=0)
    state = models.IntegerField(default=DonationState.NOT_STARTED)
    sender_token_id = models.CharField(max_length=255)
    status_code = models.CharField(max_length=255)
    error_message = models.CharField(default='', max_length=255)

    class Meta:
        abstract = True


class Donation(AmazonPayment):
    offer = models.ForeignKey(TeamOffer, related_name='donation_offer')
    

class RentVenue(AmazonPayment):
    venue = models.ForeignKey(Venue)
    
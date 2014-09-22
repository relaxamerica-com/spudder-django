from django.db import models
from spudderdomain.models import TempClub


class TempClubOtherInformation(models.Model):
    temp_club = models.ForeignKey(TempClub)
    other_information = models.TextField()

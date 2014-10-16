from django.contrib.auth.models import User
from django.db import models
from spudderdomain.models import TempClub


class TempClubOtherInformation(models.Model):
    temp_club = models.ForeignKey(TempClub)
    other_information = models.TextField()
    website = models.URLField(blank=True)
    contact_number = models.CharField(blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True)


class ChallengeServiceConfiguration(models.Model):
    SITE_UNIQUE_ID = "01"
    site_unique_id = models.CharField(max_length=256)
    time_to_complete = models.IntegerField(default=48 * 60)  # in minutes

    @classmethod
    def GetForSite(cls):
        return ChallengeServiceConfiguration.objects.get_or_create(site_unique_id=cls.SITE_UNIQUE_ID)[0]


class ChallengeServiceMessageConfiguration(models.Model):
    configuration = models.ForeignKey(ChallengeServiceConfiguration)
    notify_after = models.IntegerField()  # in minutes
    message = models.TextField()

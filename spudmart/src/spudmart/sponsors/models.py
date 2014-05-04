from django.contrib.auth.models import User
from django.db import models
from djangotoolbox.fields import ListField
from spudmart.files.models import UploadedFile


class SponsorPage(models.Model):
    sponsor = models.ForeignKey(User)
    name = models.CharField(max_length=255, blank=False)
    speciality = models.CharField(max_length=255, blank=False)
    phone = models.CharField(max_length=255, blank=False)
    fax = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    website = models.CharField(max_length=255, blank=True)
    video = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    map_info = models.CharField(max_length=255, blank=True)
    thumbnail = models.ForeignKey(UploadedFile, null=True)
    images = ListField()
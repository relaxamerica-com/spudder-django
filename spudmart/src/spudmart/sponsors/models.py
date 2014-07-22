from django.contrib.auth.models import User
from django.db import models
from djangotoolbox.fields import ListField


class SponsorPage(models.Model):
    sponsor = models.ForeignKey(User)
    name = models.CharField(max_length=255, blank=False)
    speciality = models.CharField(max_length=255, blank=False)
    phone = models.CharField(max_length=255, blank=False)
    fax = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    website = models.CharField(max_length=255, blank=True)
    video = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    map_info = models.CharField(max_length=255, blank=True)
    thumbnail = models.CharField(max_length=255, blank=True)
    facebook = models.CharField(max_length=255, blank=True)
    twitter = models.CharField(max_length=255, blank=True)
    google_plus = models.CharField(max_length=255, blank=True)
    instagram = models.CharField(max_length=255, blank=True)
    linkedin = models.CharField(max_length=255, blank=True)
    images = ListField()
    tag = models.CharField(max_length=255, blank=False)

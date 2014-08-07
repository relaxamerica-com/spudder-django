from django.db import models
import json
import datetime

# Global Models

class VenuesModel(models.Model):
    venue_id = models.CharField(max_length=20)
    lat = models.CharField(max_length=20)
    lon = models.CharField(max_length=20)


class SpudFromSocialMedia(models.Model):
    STATE_NEW = '01'
    STATE_REJECTED = '02'
    STATE_ACCEPTED = '03'
    STATE_CHOICES = (STATE_NEW, STATE_REJECTED, STATE_ACCEPTED, )

    TYPE_IMAGE = '01'
    TYPE_CHOICES = (TYPE_IMAGE, )

    version = models.CharField(max_length=1, default='01')
    entity_type = models.CharField(max_length=255)
    entity_id = models.CharField(max_length=255)
    originating_service = models.CharField(max_length=255)
    unique_id_from_source = models.CharField(max_length=256)
    state = models.CharField(max_length=2, choices=STATE_CHOICES)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    data = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)



# Instagram Specific Models

class InstagramDataProcessor(models.Model):
    venue_id = models.CharField(max_length=20)
    data = models.TextField()
    processed = models.BooleanField(default=False)
    _created_time = models.IntegerField(null=True)

    # def __init__(self):
    #     raise DeprecationWarning('this class is now depricated, please see usage of SpudFromSocialMedia')

    @property
    def created_time(self):
        if self._created_time:
            return self._created_time
        obj = json.loads(self.data)
        value = int(obj['created_time'])
        self._created_time = value
        self.save()
        return value
        
    @created_time.setter
    def created_time(self, value):
        self._created_time = value

class InstagramSubscriptions(models.Model):
    venue_id = models.CharField(max_length=20)
    subscription_id = models.CharField(max_length=20)

# Twitter Specific Models

class TwitterPolling(models.Model):
    last_poll_id = models.CharField(max_length=20)


class TwitterDataProcessor(models.Model):
    venue_id = models.CharField(max_length=20)
    data = models.TextField()
    processed = models.BooleanField(default=False)

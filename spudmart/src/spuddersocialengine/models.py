from django.db import models
import json
import datetime

# Global Models

class VenuesModel(models.Model):
    venue_id = models.CharField(max_length=20)
    lat = models.CharField(max_length=20)
    lon = models.CharField(max_length=20)

# Instagram Specific Models

class InstagramDataProcessor(models.Model):
    venue_id = models.CharField(max_length=20)
    data = models.TextField()
    processed = models.BooleanField(default=False)
    _created_time = models.IntegerField(null=True)
    
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

from django.db import models

# Global Models

class VenuesModel(models.Model) :
    venue_id = models.CharField(max_length=20)
    lat = models.CharField(max_length=20)
    lon = models.CharField(max_length=20)

# Instagram Specific Models

class InstagramDataProcessor(models.Model):
    venue_id = models.CharField(max_length=20)
    data = models.TextField()
    processed = models.BooleanField(default=False)

class InstagramSubscriptions(models.Model):
    venue_id = models.CharField(max_length=20)
    subscription_id = models.CharField(max_length=20)

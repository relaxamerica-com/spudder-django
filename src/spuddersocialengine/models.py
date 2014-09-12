import json
from django.db import models


class SpudFromSocialMedia(models.Model):
    STATE_NEW = '01'
    STATE_REJECTED = '02'
    STATE_ACCEPTED = '03'
    STATE_CHOICES = (
        (STATE_NEW, 'New'),
        (STATE_REJECTED, 'Rejected'),
        (STATE_ACCEPTED, 'Accepted'))

    TYPE_IMAGE = '01'
    TYPE_CHOICES = (
        (TYPE_IMAGE, 'Image'),)

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

    @property
    def expanded_data(self):
        return json.loads(self.data or "{}")
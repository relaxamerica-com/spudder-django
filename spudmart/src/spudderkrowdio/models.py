from django.db import models
from spudderkrowdio.utils import register_entity
from spudmart.venues.models import Venue
from django.shortcuts import get_object_or_404


class KrowdIOStorage(models.Model):
    role_id = models.CharField(max_length=256, null=True)
    role_type = models.CharField(max_length=256, null=True)  # enum based on: RoleController.ENTITY_TYPES
    venue = models.ForeignKey(Venue, null=True)
    
    krowdio_user_id = models.CharField(max_length=256)
    krowdio_access_token = models.CharField(max_length=256)
    krowdio_email = models.CharField(max_length=256)
    krowdio_access_token_expires = models.IntegerField(default=0)

    @classmethod
    def GetOrCreateForCurrentUserRole(cls, user_role):
        role_id = user_role.entity.id
        role_type = user_role.entity_type
        storage, created = KrowdIOStorage.objects.get_or_create(role_type=role_type, role_id=role_id)
        if created:
            storage._id = storage.role_id
            storage.type = storage.role_type
            register_entity(storage)
        return storage
    
    @classmethod
    def GetOrCreateForVenue(cls, venue_id):
        venue = get_object_or_404(Venue, pk = venue_id)
        storage, created = KrowdIOStorage.objects.get_or_create(venue=venue)
        if created:
            storage._id = venue.id
            storage.type = 'Venue'
            register_entity(storage)
        return storage
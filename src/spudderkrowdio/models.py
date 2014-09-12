import urllib
import logging
import settings
import simplejson
from google.appengine.api import urlfetch
from django.db import models
from django.shortcuts import get_object_or_404
from spudderdomain.models import TeamPage, FanPage
from spudmart.venues.models import Venue


FOLLOWABLE_ENTITY_TYPES = ['Venue', 'Team', 'fan']


def _post(url, data, headers={}):
    data = urllib.urlencode(data)
    result = urlfetch.fetch(url=url,
                            payload=data,
                            method=urlfetch.POST,
                            headers=headers)
    if result.status_code == 200:
        return result
    else:
        raise Exception('POST result status code different than 200: %s' % result.content)


def register_entity(entity):
    data = {
        'client_id': settings.KROWDIO_CLIENT_KEY,
        'username':  "%s%s" % (entity.type, entity._id),
        'email': "%s%s@spudder.com" % (entity.type, entity._id),
        'password': settings.KROWDIO_GLOBAL_PASSWORD
    }
    try:
        response = _post('http://auth.krowd.io/user/register', data)
        krowdio_data = simplejson.loads(response.content)
        _update_entity(entity, krowdio_data)
    except Exception as ex:
        logging.warning("krowdio.models.register_entity: Error registering entity: %s" % ex)
        if 'Email already exists' in "%s" % ex:
            logging.debug("krowdio.models.register_entity: User already exists in Krowd.io, attempting login")
            from spudderkrowdio.utils import _ensure_oAuth_token
            entity.krowdio_email = "%s%s@spudder.com" % (entity.type, entity._id)
            _ensure_oAuth_token(entity)


def _update_entity(entity, krowdio_data):
    entity.krowdio_access_token = krowdio_data['access_token']
    entity.krowdio_access_token_expires = krowdio_data['expires_in']
    entity.krowdio_user_id = krowdio_data['user']['_id']
    entity.krowdio_email = '%s@spudder.com' % krowdio_data['user']['username']
    entity.save()


class KrowdIOStorage(models.Model):
    role_id = models.CharField(max_length=256, null=True)
    role_type = models.CharField(max_length=256, null=True)  # enum based on: RoleController.ENTITY_TYPES
    venue = models.ForeignKey(Venue, null=True)
    team = models.ForeignKey(TeamPage, null=True)
    
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
    def GetOrCreateFromEntity(cls, entity_id, entity_type):
        # if there is a specific handler for this entity type then use it
        from spudderdomain.controllers import EntityController
        if entity_type == EntityController.ENTITY_VENUE:
            storage = cls.GetOrCreateForVenue(entity_id)
        elif entity_type == EntityController.ENTITY_TEAM:
            storage = cls.GetOrCreateForTeam(entity_id)
        else:
            storage, created = KrowdIOStorage.objects.get_or_create(role_type=entity_type, role_id=entity_id)
            if created:
                storage._id = storage.role_id
                storage.type = storage.role_type
                register_entity(storage)
        if not storage.krowdio_email:
            storage.role_type = entity_type
            storage._id = entity_id
            storage.type = entity_type
            storage.krowdio_email = "%s%s@spudder.com" % (entity_type, entity_id)
            register_entity(storage)
        return storage

    @classmethod
    def GetOrCreateForVenue(cls, venue_id):
        venue = get_object_or_404(Venue, pk=venue_id)
        storage, created = KrowdIOStorage.objects.get_or_create(venue=venue)
        if created:
            storage._id = venue.id
            storage.type = 'Venue'
            register_entity(storage)
        if not storage.role_type or not storage.role_id:
            storage.role_type = 'Venue'
            storage.role_id = venue_id
            storage.save()
        return storage

    @classmethod
    def GetOrCreateForTeam(cls, team_id):
        """
        Creates or gets a KrowdIOStorage object for given team
        :param team_id: a valid ID of a TeamPage object
        :return: the KrowdIOStorage object
        """
        team = get_object_or_404(TeamPage, pk=team_id)
        storage, created = KrowdIOStorage.objects.get_or_create(team=team)
        if created:
            storage._id = team.id
            storage.type = 'Team'
            register_entity(storage)
        if not storage.role_type or not storage.role_id:
            storage.role_type = 'Team'
            storage.role_id = team_id
            storage.save()
        return storage


class FanFollowingEntityTag(models.Model):
    """
    Hold the custom #tag for each entity a Fan follows

    This structure means each entity a fan follows must have a custom
    #tag, but two fans can have the same #tag for an entity to follow

    Uses the same entity_type (and IDs) as the KrowdIOStorage model
    """
    fan = models.ForeignKey(FanPage)
    tag = models.CharField(max_length=256)
    entity_id = models.CharField(max_length=256)
    entity_type = models.CharField(max_length=256)

    @classmethod
    def GetTag(cls, fan, entity_id, entity_type):
        try:
            return FanFollowingEntityTag.objects.get(
                fan=fan,
                entity_id=entity_id,
                entity_type=entity_type).tag
        except FanFollowingEntityTag.DoesNotExist:
            return None
        except FanFollowingEntityTag.MultipleObjectsReturned:
            return None
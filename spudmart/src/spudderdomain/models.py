import datetime
import json
from django.contrib.auth.models import User
from django.db import models
from djangotoolbox.fields import DictField, ListField
from spudmart.upload.models import UploadedFile
from spudmart.venues.models import SPORTS, Venue


class LinkedServiceTypeExistsForThisRole(Exception):
    pass


class LinkedService(models.Model):
    """
    Model that hold the configuration of any linked services such as Amazon, LinkedIn, Facebook etc

    *Should not be created directly, in stead, please use the Create class method provided
    """
    STATE_UNCONFIGURED = "unconfigured"
    STATE_CONFIGURED = "configured"

    LinkedServiceTypeExistsForThisRole = LinkedServiceTypeExistsForThisRole

    state = models.CharField(max_length=256, default=STATE_UNCONFIGURED)
    role_id = models.CharField(max_length=256)
    role_type = models.CharField(max_length=256)
    service_type = models.CharField(max_length=256)
    unique_service_id = models.CharField(max_length=1024)
    created = models.DateTimeField()
    _service_configuration = models.TextField()

    @classmethod
    def Create(cls, role, service_type, unique_service_id, configuration):
        """
        Creates a new LinkedService instance for the given role and service_type

        * Raises LinkedService.LinkedServiceTypeExistsForThisRole if this role is already linked to a service of this
        type

        :type service_type: enumerate spudderdomain.controllers.RoleController.ENTITY_TYPES
        :type unique_service_id: str
        :type configuration: dict
        :type role: spudderaccounts.wrappers.RoleBase
        :param cls: Class LinkedService
        :param role: Instance of the RoleBase wrapper
        :param service_type: Enum taken from LinkedServiceController.SERVICE_TYPES
        :param unique_service_id:
        :param configuration:
        :return: New instance of LinkedService
        """
        query = LinkedService.objects.filter(
            role_id=role.entity.id,
            role_type=role.entity_type,
            unique_service_id=unique_service_id,
            service_type=service_type)
        if query.count():
            raise LinkedServiceTypeExistsForThisRole
        service = LinkedService(
            role_id=role.entity.id,
            role_type=role.entity_type,
            service_type=service_type,
            unique_service_id=unique_service_id,
            created=datetime.datetime.now(),
            _service_configuration=json.dumps(configuration))
        service.save()
        return service

    @property
    def configuration(self):
        return json.loads(self._service_configuration or '{}')

    @configuration.setter
    def configuration(self, config_object):
        self._service_configuration = json.dumps(config_object or '{}')

class SpudType():
    TEXT = 1
    VIDEO = 2
    IMAGE = 3


class Comment(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User)  # what user should be used here?
    text = models.TextField()


class Spud(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    tags = ListField()
    type = models.IntegerField(choices = ((SpudType.TEXT, 'Text'),
                                          (SpudType.VIDEO, 'Video'),
                                          (SpudType.IMAGE, 'Image')), default = SpudType.TEXT)
    comments = ListField(Comment)
    content = models.TextField()
    image = models.ForeignKey(UploadedFile, null=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    author = models.ForeignKey(User)  # what user should be used here?

    def tags_to_string(self):
        return ' '.join(self.tags)
    
    
class FanPage(models.Model):
    fan = models.ForeignKey(User)
    username = models.CharField(max_length=255, blank=False)
    name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    avatar = models.ForeignKey(UploadedFile, blank=True, null=True, related_name='fanpage_avatar')
    cover_image = models.ForeignKey(UploadedFile, blank=True, null=True, related_name='fanpage_cover_image')
    free_text = models.CharField(max_length=1024, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    facebook = models.CharField(max_length=255, blank=True)
    twitter = models.CharField(max_length=255, blank=True)
    google_plus = models.CharField(max_length=255, blank=True)
    instagram = models.CharField(max_length=255, blank=True)
    linkedin = models.CharField(max_length=255, blank=True)

    def was_edited(self):
        return self.email is not None and self.email != ""


class _TeamWithNameAlreadyExistsError(Exception):
    pass


def _update_location_from_post_data(location, post_data):
    """
        :param location: Location entity for update
        :param post_data: string containing comma separated data (lat;lng;info_window;address)
        :return: updated Location entity
    """

    location.post_data = post_data

    if post_data:
        lng, lat, info_window, address = post_data.split(';')

        location.latitude = float(lat)
        location.longitude = float(lng)
        location.info_window = info_window
        location.address = address

    location.save()

    return location


class Location(models.Model):
    latitude = models.FloatField(default=0, null=True, blank=True)
    longitude = models.FloatField(default=0, null=True, blank=True)
    post_data = models.CharField(max_length=255, default='', blank=True)
    info_window = models.CharField(max_length=255, default='', blank=True)
    address = models.CharField(max_length=255, default='', blank=True)

    @staticmethod
    def from_post_data(post_data):
        location = Location()
        location = _update_location_from_post_data(location, post_data)

        return location

    def update_from_post_data(self, post_data):
        _update_location_from_post_data(self, post_data)

    @property
    def external_link(self):
        start_index = self.info_window.index('href="') + 6
        end_index = self.info_window.index(' target') - 1

        return self.info_window[start_index:end_index]

    def __unicode__(self):
        return unicode(self.address)

    def __str__(self):
        return unicode(self).encode('utf-8')


class TeamPage(models.Model):
    name = models.CharField(max_length=255)
    location = models.ForeignKey(Location, null=True, blank=True)
    contact_details = models.CharField(max_length=255, blank=True)
    free_text = models.TextField(blank=True)
    sport = models.CharField(max_length=100)
    image = models.ForeignKey(UploadedFile, null=True, blank=True)
    cover_image = models.ForeignKey(UploadedFile, blank=True, null=True, related_name='team_page_cover_image')
    state = models.CharField(max_length=2)

    TeamWithNameAlreadyExistsError = _TeamWithNameAlreadyExistsError

    def update_location(self, location_info):
        if not location_info:
            self.location = None
            return

        if not self.location:
            self.location = Location.from_post_data(location_info)
        else:
            self.location.update_from_post_data(location_info)

    def __unicode__(self):
        return unicode(self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')


class TeamAdministrator(models.Model):
    entity_type = models.CharField(max_length=255)
    entity_id = models.CharField(max_length=255)
    team_page = models.ForeignKey(TeamPage, related_name='team_administrator_team_page')


class TeamVenueAssociation(models.Model):
    team_page = models.ForeignKey(TeamPage, related_name='team_venue_team_page')
    venue = models.ForeignKey(Venue, related_name='team_venue_venue')

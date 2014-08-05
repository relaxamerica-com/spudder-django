import datetime
import json
from django.contrib.auth.models import User
from django.db import models
from djangotoolbox.fields import DictField, ListField
from spudmart.upload.models import UploadedFile
from spudmart.venues.models import SPORTS


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


class TeamPage(models.Model):
    admins = ListField(models.ForeignKey(User))
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    contact_details = models.CharField(max_length=255, blank=True)
    free_text = models.CharField(max_length=255, blank=True)
    sport = models.CharField(max_length=100)
    image = models.ForeignKey(UploadedFile, null=True)
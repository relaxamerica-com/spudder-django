import datetime
import json
from django.db import models
from djangotoolbox.fields import DictField
import spudderaccounts


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
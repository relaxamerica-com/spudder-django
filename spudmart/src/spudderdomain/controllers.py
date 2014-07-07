from spudderdomain.models import LinkedService
from spudmart.CERN.models import Student


class RoleController(object):
    """
    The RoleController offers a unified internal api for managing user roles within Spudder
    """

    ENTITY_STUDENT = "student"
    ENTITY_TYPES = (ENTITY_STUDENT, )

    @classmethod
    def GetRoleForEntityTypeAndID(cls, entity_type, entity_id, entity_wrapper):
        if entity_type == cls.ENTITY_STUDENT:
            try:
                return entity_wrapper(Student.objects.get(id=entity_id))
            except Student.DoesNotExist:
                return None
        else:
            raise NotImplementedError("The entity_type: %s is not yet supported" % entity_type)

    def __init__(self, user):
        """
        Init a new role controller based on the provided User instance

        :param user: a django.contrib.auth.models.User instance
        :return: a RoleController instance based on the provided user
        """
        self.user = user

    def roles_by_entity(self, entity_key, entity_wrapper):
        """
        Get a collection of roles of the type defined by entity_key

        :param entity_key: Enumeration from RoleController.ENETITY_, the type of role to return
        :param entity_wrapper: class derived from EntityBase
        :return: Collection of entity objects wrapper in entity_wrapper
        """
        if entity_key == self.ENTITY_STUDENT:
            roles = Student.objects.filter(user=self.user)
        else:
            raise NotImplementedError("that entity_key is not yet supported")
        roles = [entity_wrapper(r) for r in roles]
        return roles

    def role_by_entity_type_and_entity_id(self, entity_key, entity_id, entity_wrapper):
        """
        Get a given role wrapped in entity_wrapper for a given entity_key and entity_id

        :param entity_key: Enumeration from RoleController.ENETITY_, the type of role to return
        :param entity_id: The id of the entity
        :param entity_wrapper: class derived from EntityBase
        :return: Instance of the entity of type entity_type with id entity_id wrapped in entity_wrapper
        """
        if entity_key == self.ENTITY_STUDENT:
            try:
                entity = Student.objects.get(id=entity_id)
                return entity_wrapper(entity)
            except Student.DoesNotExist:
                return None
        else:
            raise NotImplementedError("that entity_key is not yet supported")


class LinkedServiceController(object):

    SERVICE_AMAZON = "amazon"
    SERVICE_TYPES = (SERVICE_AMAZON, )

    @classmethod
    def LinkedServiceByTypeAndID(cls, linked_service_type, unique_service_id, service_wrapper):
        try:
            linked_service = LinkedService.objects.get(
                service_type=linked_service_type,
                unique_service_id=unique_service_id)
            return service_wrapper(linked_service)
        except LinkedService.DoesNotExist:
            return None

    def __init__(self, role):
        self.role = role

    def create_linked_service(self, linked_service_type, unique_service_id, configuration, service_wrapper):
        linked_service = LinkedService.Create(self.role, linked_service_type, unique_service_id, configuration)
        linked_service.save()
        return service_wrapper(linked_service)

    def linked_services(self, type_filters=None):
        all_linked_services = LinkedService.objects.filter(role_type=self.role.entity_type, role_id=self.role.entity.id)
        if type_filters:
            all_linked_services = [s for s in all_linked_services if s.service_type in type_filters]
        return all_linked_services
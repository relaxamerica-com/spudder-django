from spudderdomain.models import LinkedService
from spudmart.CERN.models import Student
from spudmart.sponsors.models import SponsorPage


class RoleController(object):
    """
    The RoleController offers a unified internal api for managing user roles within Spudder
    """

    ENTITY_STUDENT = "student"
    ENTITY_SPONSOR = "sponsor"
    ENTITY_TYPES = (ENTITY_STUDENT, ENTITY_SPONSOR, )

    @classmethod
    def GetRoleForEntityTypeAndID(cls, entity_type, entity_id, entity_wrapper):
        if entity_type == cls.ENTITY_STUDENT:
            try:
                return entity_wrapper(Student.objects.get(id=entity_id))
            except Student.DoesNotExist:
                return None
        elif entity_type == cls.ENTITY_SPONSOR:
            try:
                return entity_wrapper(SponsorPage.objects.get(id=entity_id))
            except SponsorPage.DoesNotExist:
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
        elif entity_key == self.ENTITY_SPONSOR:
            roles = SponsorPage.objects.filter(sponsor=self.user)
        else:
            raise NotImplementedError("That entity_key is not yet supported")
        roles = [entity_wrapper(r) for r in roles]
        return roles

    def role_by_entity_type_and_entity_id(self, entity_key, entity_id, entity_wrapper):
        """
        Get a given role wrapped in entity_wrapper for a given entity_key and entity_id

        :param entity_key: Enumeration from RoleController.ENTITY_, the type of role to return
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
        elif entity_key == self.ENTITY_SPONSOR:
            try:
                entity = SponsorPage.objects.get(id=entity_id)
                return entity_wrapper(entity)
            except SponsorPage.DoesNotExist:
                return None
        else:
            raise NotImplementedError("That entity_key is not yet supported")


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
    

class SpudsController(object):

    def __init__(self, role, venue_id):
        self.role = role
        self.venue_id = venue_id

    def get_any_unapproved_spuds(self):
        """
        Gets any unapproved spuds linked to this role

        :return: Collection of Spuds
        """
        return [{
            'id': 1,
            'images': {
                'large': 'http://cdn.cutestpaw.com/wp-content/uploads/2013/12/l-Soccer-cat.jpg',
                'small': 'http://cdn.cutestpaw.com/wp-content/uploads/2013/12/l-Soccer-cat.jpg'
            },
            'tags': ['@Karol', '@Matt'],
            'created_time': '123'
        },
        {
         'id': 2,
         'images': {
                'large': 'https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcTdw2F_TbS2s9GJUGyyJaCug1WARReA5b9HhyKnaS-NsV8dKp-j',
                'small': 'https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcTdw2F_TbS2s9GJUGyyJaCug1WARReA5b9HhyKnaS-NsV8dKp-j'
            },
            'tags': ['@Lucy'],
            'created_time': '1235'
        },
        {
         'id': 3,
         'images': {
                'large': 'http://graphics8.nytimes.com/images/2009/06/25/sports/soccer/soccer3_600.jpg',
                'small': 'http://graphics8.nytimes.com/images/2009/06/25/sports/soccer/soccer3_600.jpg'
            },
            'tags': ['@Dennis'],
            'created_time': '12315'
        },
        {
         'id': 4,
         'images': {
                'large': 'https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcSAsRerQz8jvmWivhzthsO7Atb4L5jZyiqhdPh8epVEPjv23wSnow',
                'small': 'https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcSAsRerQz8jvmWivhzthsO7Atb4L5jZyiqhdPh8epVEPjv23wSnow'
            },
            'tags': ['@Marie'],
            'created_time': '1315'
        },
        {
         'id': 5,
         'images': {
                'large': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcThG4sHdvuflQ6lIVA60XnaZeNxdEqaeiAIIEJMygdiNBHVo4O5',
                'small': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcThG4sHdvuflQ6lIVA60XnaZeNxdEqaeiAIIEJMygdiNBHVo4O5'
            },
            'tags': ['@Karol', '@Lukasz'],
            'created_time': '13'
        }
        ]  # collection of spuds
        
        
    def approve_spuds(self, spuds):
        """
        Sends spuds off to Krowd.io tagged with the venue in this case

        :param spuds: Collection of spuds
        :return: None
        """
        pass
from spudderdomain.models import LinkedService, FanPage
from spudmart.CERN.models import Student
from spudmart.sponsors.models import SponsorPage
from spuddersocialengine.models import InstagramDataProcessor
import logging
import simplejson
from spudmart.venues.models import Venue
from spudderkrowdio.utils import post_spud
from spudderkrowdio.models import KrowdIOStorage
import datetime


class RoleController(object):
    """
    The RoleController offers a unified internal api for managing user roles within Spudder
    """

    ENTITY_STUDENT = "student"
    ENTITY_SPONSOR = "sponsor"
    ENTITY_FAN = "fan"
    ENTITY_TYPES = (ENTITY_STUDENT, ENTITY_SPONSOR, ENTITY_FAN)

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
        elif entity_type == cls.ENTITY_FAN:
            try:
                return entity_wrapper(FanPage.objects.get(id=entity_id))
            except FanPage.DoesNotExist:
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
        elif entity_key == self.ENTITY_FAN:
            roles = FanPage.objects.filter(fan=self.user)
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
        elif entity_key == self.ENTITY_FAN:
            try:
                entity = FanPage.objects.get(id=entity_id)
                return entity_wrapper(entity)
            except FanPage.DoesNotExist:
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

    def get_unapproved_spuds(self, time_range):
        """
        Gets any unapproved spuds linked to this role

        :return: Collection of Spuds
        """
        
        unapproved_spuds = {}
        latest_instagram_data = InstagramDataProcessor.objects.filter(processed=True, venue_id=self.venue_id, _created_time__range=time_range)[:10]
        for item in latest_instagram_data:
            item.processed = True
            item.save()
            unapproved_spuds[item.id] = simplejson.loads(item.data)
        
        return unapproved_spuds


    def get_unapproved_spud_by_id(self, data_id):
        """
        Gets any unapproved spuds linked to this role
        :param data_id: InstagramDataProcessor ID
        :return: Collection of Spuds
        """
        
        instagram_data = InstagramDataProcessor.objects.get(pk = data_id)
        
        return simplejson.loads(instagram_data.data)
        
        
    def approve_spuds(self, spuds, venue_id):
        """
        Sends SPUD off to Krowd.io tagged with the venue in this case

        :param spud: A single SPUD to approve
        :return: None
        """
        
        storage = KrowdIOStorage.GetOrCreateForVenue(venue_id)
        
        for spud in spuds:
            spud['tags'].append('@Venue%s' % venue_id)
            
            if 'images' in spud:
                post_spud(storage, { 'type' : 'image', 'url' : spud['images']['standard_resolution']['url'], 'title' : spud['caption']['text'], 'usertext' : ' '.join(spud['tags']) })
                
            if 'videos' in spud:
                post_spud(storage, { 'type' : 'video', 'url' : spud['videos']['standard_resolution']['url'], 'title' : spud['caption']['text'], 'usertext' : ' '.join(spud['tags']) })
            
            
    def seconds_to_date_time(self, seconds):
        return datetime.datetime.utcfromtimestamp(seconds)
    
    
    def date_time_to_seconds(self, date):
        return int((date - datetime.datetime(1970, 1, 1)).total_seconds())
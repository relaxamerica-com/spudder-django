from datetime import datetime, timedelta
from spudderdomain.models import LinkedService, FanPage, TeamPage, TeamAdministrator
from spuddersocialengine.models import SpudFromSocialMedia
from spudmart.CERN.models import Student
from spudmart.sponsors.models import SponsorPage
from spudderkrowdio.utils import post_spud, get_user_mentions_activity, get_spud_stream_for_entity
from spudderkrowdio.models import KrowdIOStorage, FanFollowingEntityTag
from spudmart.venues.models import Venue


class EntityController(object):
    ENTITY_VENUE = "Venue"
    ENTITY_TEAM = "Team"
    ENTITY_TYPES = (ENTITY_VENUE, ENTITY_TEAM, )
    
    @classmethod
    def GetEntityByTypeAndId(cls, entity_type, entity_id):
        if entity_type == cls.ENTITY_TEAM:
            try:
                TeamPage.objects.get(id=entity_id)
            except TeamPage.DoesNotExist:
                return None
        if entity_type == cls.ENTITY_VENUE:
            try:
                Venue.objects.get(id=entity_id)
            except Venue.DoesNotExist:
                return None
        return None


class RoleController(object):
    """
    The RoleController offers a unified internal api for managing user roles within Spudder
    """

    ENTITY_STUDENT = "student"
    ENTITY_SPONSOR = "sponsor"
    ENTITY_FAN = "fan"
    ENTITY_TYPES = (ENTITY_STUDENT, ENTITY_SPONSOR, ENTITY_FAN)

    @classmethod
    def GetEntityByTypeAndId(cls, entity_type, entity_id):
        if entity_type == cls.ENTITY_STUDENT:
            try:
                return Student.objects.get(id=entity_id)
            except Student.DoesNotExist:
                return None
        elif entity_type == cls.ENTITY_SPONSOR:
            try:
                return SponsorPage.objects.get(id=entity_id)
            except SponsorPage.DoesNotExist:
                return None
        elif entity_type == cls.ENTITY_FAN:
            try:
                return FanPage.objects.get(id=entity_id)
            except FanPage.DoesNotExist:
                return None
        else:
            raise NotImplementedError("The entity_type: %s is not yet supported" % entity_type)

    @classmethod
    def GetRoleForEntityTypeAndID(cls, entity_type, entity_id, entity_wrapper):
        return entity_wrapper(cls.GetEntityByTypeAndId(entity_type, entity_id))

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


class TeamsController(object):

    @classmethod
    def CreateTeam(cls, role, **kwargs):
        team = TeamPage(**kwargs)
        team.save()
        team_admin = TeamAdministrator(entity_type=role.entity_type, entity_id=role.entity.id, team_page=team)
        team_admin.save()
        return team

    @classmethod
    def TeamsAdministeredByRole(cls, role):
        team_admins = TeamAdministrator.objects.filter(entity_type=role.entity_type, entity_id=role.entity.id)
        return [ta.team_page for ta in team_admins]
    

class SpudsController(object):

    @classmethod
    def GetSpudsForFan(cls, fan_page):
        from spudderaccounts.wrappers import RoleFan
        return get_user_mentions_activity(KrowdIOStorage.GetOrCreateForCurrentUserRole(RoleFan(fan_page)))

    def __init__(self, role):
        self.role = role

    def get_unapproved_spuds(self, venue_id, filters=None):
        """
        Gets any unapproved spuds linked to this role

        :return: Collection of Spuds
        """
        DAYS_OF_THE_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        now = datetime.now().date() + timedelta(days=1)
        base_query = SpudFromSocialMedia.objects.filter(
            entity_id=venue_id,
            entity_type='VENUE',
            state=SpudFromSocialMedia.STATE_NEW)

        if filters and 'day-' in filters:
            if filters == 'day-0':
                base_query = base_query.filter(created__gt=(now - timedelta(days=1)))
            elif filters == 'day-7':
                base_query = base_query.filter(created__lt=(now - timedelta(days=7)))
            else:
                for x in range(1, 7):
                    if filters == 'day-%s' % x:
                        base_query = base_query.filter(
                            created__gt=(now - timedelta(days=x+1)),
                            created__lt=(now - timedelta(days=x)))
        unapproved_spuds = base_query.order_by('-created')[:100]
        facets = [
            {
                'name': 'by_day',
                'display_name': 'Post by day',
                'facets': [
                    {
                        'name': 'day-0',
                        'display_name': 'Posted today',
                        'count': base_query.filter(created__gt=(now - timedelta(days=1))).count()
                    },
                    {
                        'name': 'day-1',
                        'display_name': 'Posted yesterday',
                        'count': base_query.filter(
                            created__gt=(now - timedelta(days=2)),
                            created__lt=(now - timedelta(days=1))).count()
                    },
                    {
                        'name': 'day-2',
                        'display_name': 'Posted %s' % DAYS_OF_THE_WEEK[(now - timedelta(days=3)).weekday()],
                        'count': base_query.filter(
                            created__gt=(now - timedelta(days=3)),
                            created__lt=(now - timedelta(days=2))).count()
                    },
                    {
                        'name': 'day-3',
                        'display_name': 'Posted %s' % DAYS_OF_THE_WEEK[(now - timedelta(days=4)).weekday()],
                        'count': base_query.filter(
                            created__gt=(now - timedelta(days=4)),
                            created__lt=(now - timedelta(days=3))).count()
                    },
                    {
                        'name': 'day-4',
                        'display_name': 'Posted %s' % DAYS_OF_THE_WEEK[(now - timedelta(days=5)).weekday()],
                        'count': base_query.filter(
                            created__gt=(now - timedelta(days=5)),
                            created__lt=(now - timedelta(days=4))).count()
                    },
                    {
                        'name': 'day-5',
                        'display_name': 'Posted %s' % DAYS_OF_THE_WEEK[(now - timedelta(days=6)).weekday()],
                        'count': base_query.filter(
                            created__gt=(now - timedelta(days=6)),
                            created__lt=(now - timedelta(days=5))).count()
                    },
                    {
                        'name': 'day-6',
                        'display_name': 'Posted %s' % DAYS_OF_THE_WEEK[(now - timedelta(days=7)).weekday()],
                        'count': base_query.filter(
                            created__gt=(now - timedelta(days=7)),
                            created__lt=(now - timedelta(days=6))).count()
                    },
                    {
                        'name': 'day-7',
                        'display_name': 'older posts',
                        'count': base_query.filter(created__lt=(now - timedelta(days=7))).count()
                    },
                ]
            }
        ]
        return {
            'results': unapproved_spuds,
            'facets': {
                'basic_facets': facets
            },
            'pagination': {
                'total_count': base_query.count(),
                'showing': len(unapproved_spuds)
            }
        }

    def approve_spuds(self, spud_ids, venue_id):
        """
        Sends SPUD off to Krowd.io tagged with the venue in this case

        :param spud_ids: The ids of the spuds to accept
        :param venue_id: The id of the venue the spuds are tied to
        :return: None
        """
        for spud_id in spud_ids:
            spud = SpudFromSocialMedia.objects.get(id=spud_id)
            spud.state = SpudFromSocialMedia.STATE_ACCEPTED
            spud.save()
            post_spud(
                KrowdIOStorage.GetOrCreateForVenue(venue_id),
                {
                    'type': 'image',
                    'url': spud.expanded_data['image']['standard_resolution']['url'],
                    'title': ' '.join([s.encode('ascii', 'ignore') for s in spud.expanded_data['text']]),
                    'usertext': '@Venue%s' % venue_id,
                    'extra': spud.data
                })

    def add_spud_from_fan(self, spud):
        spud_text = ' '.join([s.encode('ascii', 'ignore') for s in spud.expanded_data['text']])
        tagged_entities = []
        for tag in FanFollowingEntityTag.objects.filter(fan=self.role.entity):
            if tag.tag and tag.tag in spud_text:
                tagged_entities.append("@%s%s" % (tag.entity_type, tag.entity_id))
        data = {
            'type': 'image',
            'url': spud.expanded_data['image']['standard_resolution']['url'],
            'title': spud_text,
            'usertext': '@%s%s %s' % (RoleController.ENTITY_FAN, self.role.entity.id, ' '.join(tagged_entities)),
            'extra': spud.data}
        krowd_io_storage = KrowdIOStorage.GetOrCreateForCurrentUserRole(self.role)
        post_spud(krowd_io_storage, data)
        spud.state = SpudFromSocialMedia.STATE_ACCEPTED
        spud.save()

    def reject_spuds(self, spud_ids):
        """
        Rejects potential spuds

        :param spud_ids: The ids of the spuds to reject
        :return: None
        """
        for spud_id in spud_ids:
            spud = SpudFromSocialMedia.objects.get(id=spud_id)
            spud.state = SpudFromSocialMedia.STATE_REJECTED
            spud.save()

    def seconds_to_date_time(self, seconds):
        return datetime.utcfromtimestamp(seconds)

    def date_time_to_seconds(self, date):
        return int((date - datetime(1970, 1, 1)).total_seconds())

    def get_spud_stream(self):
        return get_spud_stream_for_entity(KrowdIOStorage.GetOrCreateForCurrentUserRole(self.role))
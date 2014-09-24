import datetime
import abc
from spudderdomain.controllers import RoleController, LinkedServiceController, EntityController
from spudderdomain.models import LinkedService
from spudderdomain.wrappers import EntityBase, LinkedServiceBase, EntityTeam
from spudderkrowdio.models import FanFollowingEntityTag


"""
    Roles
        Roles are the generic name given to the different types of entities within the Spudder ecosystem. These
        can include, Students in CERN, Sponsors, Players, Fans etc.

        Each Role should be based on the RoleBase base class and must implement all abstract methods and properties
        from that class.
"""


class RoleBase(EntityBase):
    @classmethod
    def RoleWrapperByEntityType(cls, entity_key):
        if entity_key == RoleController.ENTITY_STUDENT:
            return RoleStudent
        elif entity_key == RoleController.ENTITY_SPONSOR:
            return RoleSponsor
        elif entity_key == RoleController.ENTITY_FAN:
            return RoleFan
        elif entity_key == RoleController.ENTITY_CLUB_ADMIN:
            return RoleClubAdmin
        else:
            raise NotImplementedError("the entity_key %s is not supported yet." % entity_key)

    @abc.abstractproperty
    def user(self):
        pass

    @abc.abstractproperty
    def title(self):
        pass

    @abc.abstractproperty
    def subtitle(self):
        pass

    @abc.abstractproperty
    def meta_data(self):
        pass

    @abc.abstractproperty
    def breadcrumb_name(self):
        pass

    @abc.abstractproperty
    def home_page_path(self):
        return '/'

    @abc.abstractproperty
    def home_domain(self):
        raise NotImplementedError

    @abc.abstractproperty
    def is_following_other_entities(self):
        return False

    @abc.abstractmethod
    def get_following_entities_by_entity_type(self, entity_type):
        return []

    @abc.abstractmethod
    def user_is_owner(self, user):
        pass

    def is_admin(self, entity_id, entity_type):
        raise NotImplemented("Not supported by RoleBase")


class RoleStudent(RoleBase):
    @property
    def user(self):
        return self.entity.user

    @property
    def _amazon_id(self):
        return LinkedService.objects.get(
            role_id=self.entity.id,
            role_type=self.entity_type,
            service_type=LinkedServiceController.SERVICE_AMAZON).configuration.get('amazon_user_email')

    @property
    def entity_type(self):
        return RoleController.ENTITY_STUDENT

    @property
    def image(self):
        if self.entity.logo:
            return '/file/serve/%s' % self.entity.logo.id
        else:
            return '/static/img/spuddercern/button-cern-medium.png'

    @property
    def title(self):
        return '<abbr title="Associated with %s">Student</abbr> in ' \
               '<abbr title="Campus Entrepreneur Recruiting Network">CERN</abbr> with Amazon ID %s' % (
               self.entity.school.name, self._amazon_id)

    @property
    def subtitle(self):
        return 'Tied to Amazon ID: %s <br /> School: %s' % (
            self._amazon_id,
            self.entity.school.name)

    @property
    def meta_data(self):
        return {
            'last_accessed': datetime.datetime.now()
        }

    @property
    def breadcrumb_name(self):
        return "Student: %s (%s)" % (
            self._amazon_id,
            self.entity.school.name)

    @property
    def home_page_path(self):
        return '/cern'

    @property
    def home_domain(self):
        return 'cern'

    @property
    def icon(self):
        if self.entity.logo:
            return '/file/serve/%s' % self.entity.logo.id
        else:
            return '/static/img/spuddercern/button-cern-tiny.png'

    @property
    def contact_emails(self):
        raise NotImplementedError()

    def user_is_owner(self, user):
        return self.entity.user == user


class RoleSponsor(RoleBase):
    @property
    def user(self):
        return self.entity.sponsor

    @property
    def _amazon_id(self):
        return LinkedService.objects.get(
            role_id=self.entity.id,
            role_type=self.entity_type,
            service_type=LinkedServiceController.SERVICE_AMAZON).configuration.get('amazon_user_email')

    @property
    def entity_type(self):
        return RoleController.ENTITY_SPONSOR

    @property
    def image(self):
        if self.entity.thumbnail:
            return '/file/serve/%s' % self.entity.thumbnail

        return '/static/img/spuddersponsors/button-sponsors-medium.png'

    @property
    def title(self):
        role_title = '<abbr title="Renting %s venues">Sponsor</abbr> on '
        role_title += 'Spudder with Amazon ID %s' % self._amazon_id

        return role_title

    @property
    def subtitle(self):
        role_subtitle = 'Tied to Amazon ID: %s <br /> Rented Venues: %s' % (
            self._amazon_id,
            len(self.entity.sponsorships())
        )

        return role_subtitle

    @property
    def meta_data(self):
        return {
            'last_accessed': datetime.datetime.now()
        }

    @property
    def breadcrumb_name(self):
        return "Sponsor: %s" % self._amazon_id

    @property
    def home_page_path(self):
        return '/sponsor'

    @property
    def home_domain(self):
        return 'sponsor'

    @property
    def icon(self):
        if self.entity.thumbnail:
            return '/file/serve/%s' % self.entity.thumbnail
        else:
            return '/static/img/spuddersponsors/button-sponsors-tiny.png'

    @property
    def contact_emails(self):
        raise NotImplementedError()

    def user_is_owner(self, user):
        return self.entity.user == user

    def get_amazon_id(self):
        return self._amazon_id


class RoleFan(RoleBase):
    @property
    def user(self):
        return self.entity.fan

    @property
    def entity_type(self):
        return RoleController.ENTITY_FAN

    @property
    def image(self):
        if self.entity.avatar:
            return '/file/serve/%s' % self.entity.avatar.id

        return '/static/img/spudderspuds/button-fans-medium.png'

    @property
    def title(self):
        return '<abbr title="Fan %s">Fan</abbr> with email: %s' % (self.user, self.user.email)

    @property
    def subtitle(self):
        role_subtitle = ''
        return role_subtitle

    @property
    def meta_data(self):
        return {
            'last_accessed': datetime.datetime.now()
        }

    @property
    def breadcrumb_name(self):
        return "Fan: %s" % self.user.email

    @property
    def home_page_path(self):
        return '/spuds'

    @property
    def home_domain(self):
        return 'fan'

    @property
    def is_following_other_entities(self):
        return bool(FanFollowingEntityTag.objects.filter(fan=self.entity))

    @property
    def icon(self):
        if self.entity.avatar:
            return '/file/serve/%s' % self.entity.avatar.id
        else:
            return '/static/img/spudderspuds/button-fans-tiny.png'

    @property
    def contact_emails(self):
        return [self.entity.fan.email] if self.entity.fan.email else []

    @property
    def jumbotron(self):
        if self.entity.cover_image:
            return '/file/serve/%s' % self.entity.cover_image.id

    @property
    def link_to_public_page(self):
        return '/fan/%s' % self.entity.id

    @property
    def name(self):
        return self.entity.name

    @property
    def state(self):
        return self.entity.state

    def user_is_owner(self, user):
        return self.entity.fan == user

    def get_following_entities_by_entity_type(self, entity_type=None):
        tags_and_entities = []
        for tag in FanFollowingEntityTag.objects.filter(fan=self.entity):
            if entity_type and not entity_type == tag.entity_type:
                continue
            if tag.entity_type == EntityController.ENTITY_TEAM:
                tags_and_entities.append({
                    'tag': tag.tag,
                    'entity': EntityController.GetWrappedEntityByTypeAndId(
                        tag.entity_type, tag.entity_id, EntityTeam)
                })
            if tag.entity_type == RoleController.ENTITY_FAN:
                tags_and_entities.append({
                    'tag': tag.tag,
                    'entity': RoleController.GetRoleForEntityTypeAndID(
                        tag.entity_type, tag.entity_id, RoleFan)
                })
        return tags_and_entities


class RoleClubAdmin(RoleBase):
    @property
    def user(self):
        return self.entity.admin

    @property
    def _amazon_id(self):
        return LinkedService.objects.get(
            role_id=self.entity.id,
            role_type=self.entity_type,
            service_type=LinkedServiceController.SERVICE_AMAZON).configuration.get('amazon_user_email')

    @property
    def entity_type(self):
        return RoleController.ENTITY_CLUB_ADMIN

    @property
    def image(self):
        if self.entity.club.thumbnail:
            return '/file/serve/%s' % self.entity.club.thumbnail

        return '/static/img/spudderclubs/button-clubs-medium.png'

    @property
    def title(self):
        role_title = '<abbr>Club Administrator</abbr> on '
        role_title += 'Spudder with Amazon ID %s' % self._amazon_id

        return role_title

    @property
    def subtitle(self):
        role_subtitle = 'Tied to Amazon ID: %s' % self._amazon_id

        return role_subtitle

    @property
    def meta_data(self):
        return {
            'last_accessed': datetime.datetime.now()
        }

    @property
    def breadcrumb_name(self):
        return "Club: %s" % self._amazon_id

    @property
    def home_page_path(self):
        return '/club/dashboard'

    @property
    def home_domain(self):
        return 'club'

    @property
    def icon(self):
        if self.entity.club.thumbnail:
            return '/file/serve/%s' % self.entity.club.thumbnail.id
        else:
            return '/static/img/spudderclubs/button-clubs-tiny.png'

    @property
    def contact_emails(self):
        raise NotImplementedError()


"""
    AuthenticationServices
        Authentication services are linked providers of authentication such as 'login with amazon', 'login with
        facebook' etc.

        Each Authentication service must be based on the AuthenticationServiceBase class and implement all abstract
        methods and properties from this class.
"""


class AuthenticationServiceBase(LinkedServiceBase):
    AUTHENTICATION_SERVICE_TYPES = (LinkedServiceController.SERVICE_AMAZON, )

    @classmethod
    def RoleWrapperByEntityType(cls, service_type):
        if service_type == LinkedServiceController.SERVICE_AMAZON:
            return AmazonAuthenticationService
        else:
            raise NotImplementedError("the service_type %s is not supported yet." % service_type)


class AmazonAuthenticationService(AuthenticationServiceBase):
    @property
    def user_password(self):
        return self.linked_service.configuration.get('amazon_user_id', None)

    def update_amazon_access_token(self, access_token):
        linked_service = self.linked_service
        configuration = linked_service.configuration
        configuration['access_token'] = access_token
        linked_service.configuration = configuration
        linked_service.save()
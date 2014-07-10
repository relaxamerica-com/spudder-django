import datetime
import abc
from spudderdomain.controllers import RoleController, LinkedServiceController
from spudderdomain.models import LinkedService
from spudderdomain.wrappers import EntityBase, LinkedServiceBase

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
        else:
            raise NotImplementedError("the entity_key %s is not supported yet." % entity_key)

    @abc.abstractproperty
    def user(self):
        pass

    @abc.abstractproperty
    def entity_type(self):
        pass

    @abc.abstractproperty
    def image(self):
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

    @abc.abstractmethod
    def user_is_owner(self, user):
        pass


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
        return '/static/img/spuddercern/button-cern-small.png'

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

        return '/static/img/spuddercern/button-cern-small.png'

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
        return '/dashboard'

    def user_is_owner(self, user):
        return self.entity.user == user


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
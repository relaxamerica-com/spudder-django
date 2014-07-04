import datetime
import abc
from spudderdomain.controllers import RoleController, LinkedServiceController
from spudmart.accounts.models import UserProfile
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
        else:
            raise NotImplementedError("the entity_key %s is not supported yet." % entity_key)

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

    @abc.abstractmethod
    def user_is_owner(self, user):
        pass


class RoleStudent(RoleBase):
    @property
    def _amazon_id(self):
        return UserProfile.objects.get(user=self.entity.user).amazon_id

    @property
    def entity_type(self):
        return RoleController.ENTITY_STUDENT

    @property
    def image(self):
        return '/static/img/spuddercern/button-cern-small.png'

    @property
    def title(self):
        return '<abbr title="Accociated with %s">Student</abbr> in ' \
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
            UserProfile.objects.get(user=self.entity.user).amazon_id,
            self.entity.school.name)

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
    pass
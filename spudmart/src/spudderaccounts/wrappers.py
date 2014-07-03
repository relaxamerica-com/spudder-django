import datetime
import abc
from spudderdomain.controllers import RoleController
from spudmart.accounts.models import UserProfile
from spudderdomain.wrappers import EntityBase


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
    def links(self):
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
    def links(self):
        return {
            'role_management_url': '/users/roles/student/%s' % self.entity.id
        }

    @property
    def breadcrumb_name(self):
        return "Student: %s (%s)" % (
            UserProfile.objects.get(user=self.entity.user).amazon_id,
            self.entity.school.name)

    def user_is_owner(self, user):
        return self.entity.user == user
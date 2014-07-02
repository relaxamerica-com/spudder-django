import datetime
import abc
from spudmart.accounts.models import UserProfile


class EntityBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, entity):
        self.entity = entity

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

    @abc.abstractproperty
    def user_is_owner(self, user):
        pass


class EntityStudent(EntityBase):

    @property
    def image(self):
        return '/static/img/spuddercern/button-cern-small.png'

    @property
    def title(self):
        return 'Student in <abbr title="Campus Entrepreneur Recruiting Network">CERN</abbr>'

    @property
    def subtitle(self):
        return 'Tied to Amazon ID: %s <br /> School: %s' % (
            UserProfile.objects.get(user=self.entity.user).amazon_id,
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
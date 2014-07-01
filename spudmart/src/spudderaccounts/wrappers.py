import datetime
from spudmart.accounts.models import UserProfile


class EntityStudent(object):

    def __init__(self, entity):
        self.student = entity

    @property
    def image(self):
        return '/static/img/spuddercern/button-cern-small.png'

    @property
    def title(self):
        return 'Student in <abbr title="Campus Entrepreneur Recruiting Network">CERN</abbr>'

    @property
    def subtitle(self):
        return 'Tied to Amazon ID: %s' % UserProfile.objects.get(user=self.student.user).amazon_id

    @property
    def meta_data(self):
        return {
            'last_accessed': datetime.datetime.now()
        }

    @property
    def links(self):
        return {
            'role_management_url': '/users/roles/student/%s' % self.student.id
        }
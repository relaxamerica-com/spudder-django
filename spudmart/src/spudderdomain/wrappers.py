import abc
from spudderdomain.utils import get_entity_base_instanse_by_id_and_type
from spudmart.utils.querysets import get_object_or_none


class EntityBase(object):
    """
    Base class for all entity wrappers
    """
    def __init__(self, entity):
        self._entity = entity

    @property
    def entity(self):
        return self._entity

    @abc.abstractproperty
    def entity_type(self):
        pass

    @abc.abstractproperty
    def image(self):
        pass

    @abc.abstractproperty
    def icon(self):
        pass

    @abc.abstractproperty
    def contact_emails(self):
        pass

    @classmethod
    def EntityWrapperByEntityType(cls, entity_key):
        from spudderdomain.controllers import EntityController
        if entity_key == EntityController.ENTITY_TEAM:
            return EntityTeam
        elif entity_key == EntityController.ENTITY_VENUE:
            return EntityVenue
        else:
            raise NotImplementedError("the entity_key %s is not supported yet." % entity_key)

    @abc.abstractmethod
    def is_admin(self, entity_id, entity_type):
        pass


class EntityVenue(EntityBase):

    @property
    def entity_type(self):
        from spudderdomain.controllers import EntityController
        return EntityController.ENTITY_VENUE

    @property
    def icon(self):
        if self.entity.logo:
            return '/file/serve/%s' % self.entity.logo.id
        else:
            return '/static/img/spuddervenues/button-venues-tiny.png'

    @property
    def image(self):
        if self.entity.logo:
            return '/file/serve/%s' % self.entity.logo.id
        else:
            return '/static/img/spuddervenues/button-venues-medium.png'

    @property
    def contact_emails(self):
        raise NotImplementedError()


class EntityTeam(EntityBase):

    @property
    def entity_type(self):
        from spudderdomain.controllers import EntityController
        return EntityController.ENTITY_TEAM

    @property
    def icon(self):
        if self.entity.image:
            return '/file/serve/%s' % self.entity.image.id
        else:
            return '/static/img/spudderspuds/button-teams-tiny.png'

    @property
    def image(self):
        if self.entity.image:
            return '/file/serve/%s' % self.entity.image.id
        else:
            return '/static/img/spudderspuds/button-teams-medium.png'

    @property
    def contact_emails(self):
        from spudderdomain.models import TeamAdministrator
        team_admins = TeamAdministrator.objects.filter(team_page=self.entity)
        contact_emails = []
        for team_admin in team_admins:
            entity = get_entity_base_instanse_by_id_and_type(team_admin.entity_id, team_admin.entity_type)
            contact_emails += entity.contact_emails
        return contact_emails

    def is_admin(self, entity_id, entity_type):
        from spudderdomain.models import TeamAdministrator
        return get_object_or_none(TeamAdministrator, entity_type=entity_type,
                                  entity_id=entity_id, team_page=self.entity) is not None


class LinkedServiceBase(object):
    """
    Base class for all Linked Service wrappers
    """
    def __init__(self, linked_service):
        self._linked_service = linked_service

    @property
    def linked_service(self):
        return self._linked_service
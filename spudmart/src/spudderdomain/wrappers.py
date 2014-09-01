import abc


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


class LinkedServiceBase(object):
    """
    Base class for all Linked Service wrappers
    """
    def __init__(self, linked_service):
        self._linked_service = linked_service

    @property
    def linked_service(self):
        return self._linked_service
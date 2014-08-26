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


class EntityVenue(EntityBase):

    @property
    def entity_type(self):
        from spudderdomain.controllers import EntityController
        return EntityController.ENTITY_VENUE


class EntityTeam(EntityBase):

    @property
    def entity_type(self):
        from spudderdomain.controllers import EntityController
        return EntityController.ENTITY_TEAM


class LinkedServiceBase(object):
    """
    Base class for all Linked Service wrappers
    """
    def __init__(self, linked_service):
        self._linked_service = linked_service

    @property
    def linked_service(self):
        return self._linked_service
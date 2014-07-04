class EntityBase(object):
    """
    Base class for all entity wrappers
    """
    def __init__(self, entity):
        self._entity = entity

    @property
    def entity(self):
        return self._entity


class LinkedServiceBase(object):
    """
    Base class for all Linked Service wrappers
    """
    def __init__(self, linked_service):
        self._linked_service = linked_service

    @property
    def linked_service(self):
        return self._linked_service
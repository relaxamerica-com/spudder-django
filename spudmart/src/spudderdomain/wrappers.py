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

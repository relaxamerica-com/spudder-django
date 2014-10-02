import abc
from spudderdomain.models import ClubAdministrator
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
    def jumbotron(self):
        raise NotImplementedError

    @abc.abstractproperty
    def contact_emails(self):
        pass

    @abc.abstractproperty
    def link_to_public_page(self):
        raise NotImplementedError

    @abc.abstractproperty
    def name(self):
        raise NotImplementedError

    @abc.abstractproperty
    def state(self):
        raise NotImplementedError

    @classmethod
    def EntityWrapperByEntityType(cls, entity_key):
        from spudderdomain.controllers import EntityController
        if entity_key == EntityController.ENTITY_TEAM:
            return EntityTeam
        elif entity_key == EntityController.ENTITY_VENUE:
            return EntityVenue
        elif entity_key == EntityController.ENTITY_CLUB:
            return EntityClub
        elif entity_key == EntityController.ENTITY_TEMP_CLUB:
            return EntityTempClub
        elif entity_key == EntityController.ENTITY_AFFILIATE:
            return EntityAffiliate
        else:
            raise NotImplementedError("the entity_key %s is not supported yet." % entity_key)

    @abc.abstractmethod
    def is_admin(self, entity_id, entity_type):
        pass

    @abc.abstractproperty
    def affiliate(self):
        pass


class EntityAffiliate(EntityBase):
    @property
    def entity_type(self):
        from spudderdomain.controllers import EntityController
        return EntityController.ENTITY_AFFILIATE

    @property
    def icon(self):
        if self.entity.path_to_icon != "":
            return self.entity.path_to_icon
        else:
            return '/static/img/spudderclubs/button-clubs-tiny.pny'

    @property
    def image(self):
        if self.entity.path_to_icon != "":
            return self.entity.path_to_icon
        else:
            return '/static/img/spudderclubs/button-clubs-tiny.pny'

    @property
    def jumbotron(self):
        if self.entity.path_to_cover_image != "":
            return self.entity.path_to_cover_image
        else:
            return None

    @property
    def contact_emails(self):
        raise NotImplementedError()

    @property
    def link_to_public_page(self):
        return "/%s" % self.entity.url_name

    @property
    def name(self):
        return self.entity.name

    @property
    def state(self):
        raise NotImplementedError()

    def is_admin(self, entity_id, entity_type):
        raise NotImplementedError()

    @property
    def affiliate(self):
        return self.entity


class EntityTempClub(EntityBase):
    @property
    def entity_type(self):
        from spudderdomain.controllers import EntityController

        return EntityController.ENTITY_TEMP_CLUB

    @property
    def icon(self):
        return '/static/img/spudderclubs/button-clubs-tiny.pny'

    @property
    def image(self):
        return '/static/img/spudderclubs/button-clubs-tiny.pny'

    @property
    def jumbotron(self):
        raise NotImplementedError()

    @property
    def contact_emails(self):
        return [self.entity.email]

    @property
    def link_to_public_page(self):
        return None

    @property
    def name(self):
        return self.entity.name

    @property
    def state(self):
        return self.entity.state

    def is_admin(self, entity_id, entity_type):
        raise NotImplementedError()

    @property
    def affiliate(self):
        return self.entity.affiliate


class EntityClub(EntityBase):
    @property
    def entity_type(self):
        from spudderdomain.controllers import EntityController
        return EntityController.ENTITY_CLUB

    @property
    def icon(self):
        return '/static/img/spudderclubs/button-clubs-tiny.pny'

    @property
    def image(self):
        return '/static/img/spudderclubs/button-clubs-tiny.pny'

    @property
    def jumbotron(self):
        raise NotImplementedError

    @property
    def contact_emails(self):
        emails = []
        for admin in ClubAdministrator.objects.filter(club=self.entity):
            emails.append(admin.admin.email)
        return emails

    @property
    def link_to_public_page(self):
        return '/clubs/%s' % self.entity.id

    @property
    def name(self):
        return self.entity.name

    @property
    def state(self):
        return self.entity.state

    def is_admin(self, entity_id, entity_type):
        raise NotImplementedError

    @property
    def affiliate(self):
        raise NotImplementedError


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
    def jumbotron(self):
        if self.entity.cover_image:
            return '/file/serve/%s' % self.entity.cover_image.id

    @property
    def contact_emails(self):
        raise NotImplementedError()

    @property
    def link_to_public_page(self):
        return '/venues/view/%s' % self.entity.id
    
    @property
    def name(self):
        return self.entity.aka_name

    @property
    def state(self):
        return self.entity.state

    def is_admin(self, entity_id, entity_type):
        raise NotImplementedError()

    @property
    def affiliate(self):
        return self.entity.affiliate


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
    def jumbotron(self):
        if self.entity.cover_image:
            return '/file/serve/%s' % self.entity.cover_image.id

    @property
    def contact_emails(self):
        from spudderdomain.models import TeamAdministrator
        team_admins = TeamAdministrator.objects.filter(team_page=self.entity)
        contact_emails = []
        for team_admin in team_admins:
            entity = get_entity_base_instanse_by_id_and_type(team_admin.entity_id, team_admin.entity_type)
            contact_emails += entity.contact_emails
        return contact_emails

    @property
    def link_to_public_page(self):
        return '/team/%s' % self.entity.id

    @property
    def name(self):
        return self.entity.name

    @property
    def state(self):
        return self.entity.state

    def is_admin(self, entity_id, entity_type):
        from spudderdomain.models import TeamAdministrator
        return get_object_or_none(TeamAdministrator, entity_type=entity_type,
                                  entity_id=entity_id, team_page=self.entity) is not None

    @property
    def affiliate(self):
        return self.entity.affiliate


class LinkedServiceBase(object):
    """
    Base class for all Linked Service wrappers
    """
    def __init__(self, linked_service):
        self._linked_service = linked_service

    @property
    def linked_service(self):
        return self._linked_service